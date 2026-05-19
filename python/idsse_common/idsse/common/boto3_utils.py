"""List directories and retrieve s3 objects from S3 buckets that (may) require authentication"""

# -------------------------------------------------------------------------------
# Created on Tue Apr 28 2026
#
# Copyright (c) 2026 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# -------------------------------------------------------------------------------

import logging
import os
from collections.abc import Sequence
from datetime import datetime, timedelta

import boto3
import botocore.credentials

from .protocol_utils import ProtocolUtils

logger = logging.getLogger(__name__)


class Boto3Utils(ProtocolUtils):
    """Boto3 (AWS) utility class that supports AWS IAM authentication"""

    PROTOCOL = "s3://"

    def __init__(self, basedir: str, subdir: str, file_base: str, file_ext: str):
        # create new Session which holds AWS IAM Tokens, if needed, to authenticate with S3 bucket
        self._session = AwsSession()
        super().__init__(basedir, subdir, file_base, file_ext)

    @property
    def credentials(self) -> botocore.credentials.Credentials | None:
        """Current AWS Credentials dictionary for this active Session, if IAM Role assumed. None if
        no AWS_* environment variables present (bucket doesn't require manual IAM Role)
        """
        return self._session.credentials

    def ls(self, path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the AWS s3 bucket specified by path

        Args:
            path (str): path to S3 bucket directory, e.g. s3://my-bucket/
            prepend_path (bool): Add the full s3 bucket path to any returned filenames.
                Defaults to True.

        Returns:
            Sequence[str]: The results sent to stdout from executing a 'ls' on passed path
        """
        if path[-1] != "/":
            path = path + "/"  # ensure a trailing slash, which is expected by S3

        # example: (s3://my-bucket-name/deeply/nested/object/here.txt)
        # ignore protocol (s3://), then everything up until the first / is the bucket name
        bucket, prefix = path.replace(self.PROTOCOL, "").split("/", maxsplit=1)
        s3 = self._session.client("s3")
        try:
            response: dict = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")
        except PermissionError:
            return []

        # boto3 returns children under .zarr directory as well as *.zarr/; combine any files
        # and directories at this level into general "objects"
        found_objects: list[str] = [
            file["Prefix"] for file in response.get("CommonPrefixes", [])
        ] + [file["Key"] for file in response.get("Contents", [])]

        if prepend_path:
            return [os.path.join(self.PROTOCOL, bucket, obj) for obj in found_objects]
        # boto3 returns full object path; drop everything except last level
        return [file.split("/")[-1] for file in found_objects]

    def cp(self, path: str, dest: str) -> bool:
        """Execute a 'cp' on the AWS s3 bucket specified by path, destination. Note: this uses the
        basic `boto3.download_file()` and may be quite slow.

        Args:
            path (str): Relative or Absolute path to the object to be copied
            dest (str): The destination location

        Returns:
            bool: Returns True if copy is successful
        """
        if path[-1] != "/":
            path = path + "/"  # ensure a trailing slash, which is expected by S3

        # ignore protocol (s3://), then everything up until the first / is the bucket name
        bucket, object_key = path.replace(self.PROTOCOL, "").split("/", maxsplit=1)

        s3 = self._session.client("s3")
        try:
            s3.download_file(Bucket=bucket, Key=object_key, Filename=dest)
            return True
        except PermissionError:
            return False


class AwsSession:
    """Persist an AWS session in memory, refreshing credentials when needed"""

    REQUIRED_ENV_VARS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_ROLE_ARN"]

    def __init__(self):
        """Create AWS boto3 Session to reuse IAM credentials with repeated AWS API (e.g. S3) calls.
        Requires environment variables AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_ROLE_ARN,
        which will be used to assume an IAM Role that has the API permissions needed.

        Any boto3 object returned from `client()`, `resource()`, or `credentials` is guaranteed to
        have fresh credentials, reusing locally-cached credentials when possible or renewing them
        with AWS.
        """
        self._session: boto3.Session | None = None
        # expiration datetime of current Session. Inits as the epoch (null Session always expired)
        self._expiration = datetime(1970, 1, 1)

    def is_expired(self) -> bool:
        """Returns True if the current boto3 Session object is expired"""
        # don't use .now(UTC), because AWS returns expiration as local datetime
        return self._expiration.timestamp() <= datetime.now().timestamp()

    def client(self, *args, **kwargs):
        """Get a boto3 client, such as 'sqs' or 's3', with guaranteed fresh AWS credentials"""
        return self.fetch_session().client(*args, **kwargs)

    def resource(self, *args, **kwargs):
        """Get a boto3 resource, such as 'dynamodb', with guaranteed fresh AWS credentials"""
        return self.fetch_session().resource(*args, **kwargs)

    def fetch_session(self) -> boto3.Session | None:
        """Get AWS boto3 Session cached in memory, or create new one if needed. From this object, a
        client to any service (e.g. SQS) can be created with `session.client(<AWS service>)`.

        Implicitly relies on secrets like AWS_ACCESS_KEY_ID, AWS_SECRET_KEY, AWS_ROLE_ARN.
        """
        if not self._session:
            # session does not exist, so must make a new one by assuming the role in _role_arn
            # note that we also save the expiration time, to catch the second the Session expires
            self._session, self._expiration = self._assume_role()

        if self.is_expired():
            logging.info("AWS SessionToken is expired, refreshing now")
            self._session, self._expiration = self._assume_role()

        return self._session

    @property
    def credentials(self) -> botocore.credentials.Credentials | None:
        """Current AWS Credentials dictionary for this active Session, if IAM Role assumed.

        Returns:
            (botocore.credentials.Credentials): the credentials of the current Session, guaranteed
                to not be expired (already refreshed if necessary).
        """
        # confirm we have all AWS env vars needed to assume IAM role. If some are missing, assume
        # caller does not need an AWS Session in this environment
        for required_var in self.REQUIRED_ENV_VARS:
            if not os.getenv(required_var):
                logger.debug(
                    "Missing expected AWS env var %s, skipping AWS IAM session", required_var
                )
                return None

        return self.fetch_session().get_credentials()

    @staticmethod
    def _assume_role() -> tuple[boto3.Session, datetime]:
        """
        Assume role specified by `role_arn`, in AWS region `region` and creates new Session.

        Returns:
            tuple[boto3.Session, datetime]: Session object (with fresh credentials) and expiration.
        """
        region = os.getenv("AWS_REGION", "us-east-1")

        # create session using access keys (may be for an AWS User), then use those temporary
        # user credentials to assume the associated Role
        sts = boto3.client(
            "sts",
            region_name=region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        # infer the role ARN attached to the access key ID in our environment
        caller_identity: dict = sts.get_caller_identity()

        # may not need ARN at all, if running on assumed role like on an EC2, e.g.
        # arn:aws:iam:<account>:assumed-role/<role_name>/i-12345
        if "assumed-role" in caller_identity["Arn"]:
            # HACK: how to look up sts expiration? this blindly refreshes once every 30 minutes
            expiration = datetime.now() + timedelta(minutes=30)
            return (boto3.Session(region_name=region), expiration)

        role_arn = os.getenv("AWS_ROLE_ARN")
        logger.debug("Assuming AWS role from environment variable: %s", role_arn)

        assumed_role = sts.assume_role(RoleArn=role_arn, RoleSessionName="idss-engine-instance")
        creds: dict = assumed_role["Credentials"]

        return (
            boto3.Session(
                region_name=region,
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"],
            ),
            creds["Expiration"],
        )

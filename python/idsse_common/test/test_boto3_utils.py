"""Test suite for boto3_utils.py"""

# ----------------------------------------------------------------------------------
# Created on Wed Apr 29 2026
#
# Copyright (c) 2026 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name
# pylint: disable=invalid-name,unused-argument

from copy import deepcopy
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock

import boto3
from pytest import fixture, MonkeyPatch

from idsse.common.boto3_utils import AwsSession

# constants
EXAMPLE_ACCOUNT_ID = "123456789012"
EXAMPLE_REGION = "us-east-1"
EXAMPLE_ROLE_ARN = "arn:aws:sts::123456789012:assumed-role/my-role"
EXAMPLE_EXPIRATION = datetime(2025, 9, 19, 23, 7, 3)
EXAMPLE_NOW = datetime(2025, 9, 19, 16, 15, 30)

ASSUME_ROLE_RESPONSE = {
    "Credentials": {
        "AccessKeyId": "my_key_id",
        "SecretAccessKey": "my_secret_access_key",
        "SessionToken": "some_long_session_token/H3OI=",
        "Expiration": EXAMPLE_EXPIRATION,
    },
    "AssumedRoleUser": {
        "AssumedRoleId": "ROLEARN123:windninja_windcast",
        "Arn": f"{EXAMPLE_ROLE_ARN}/windninja_windcast",
    },
    "ResponseMetadata": {
        "RequestId": "f9f0abde-18e5-4a33-a6ba-91bb50c8a122",
        "HTTPStatusCode": 200,
        "RetryAttempts": 0,
    },
}
CALLER_IDENTITY_RESPONSE = {
    "UserId": "AIDARA4W2CFC6Z6KMZ7QB",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/my-user",
    "ResponseMetadata": {
        "RequestId": "5404258e-57fd-49fd-acd0-1121313b8922",
        "HTTPStatusCode": 200,
        "RetryAttempts": 0,
    },
}

EXAMPLE_ISSUE = datetime(1970, 10, 3, 12, tzinfo=UTC)
EXAMPLE_VALID = datetime(1970, 10, 3, 14, tzinfo=UTC)

EXAMPLE_BUCKET = "gsl-desi-2"
EXAMPLE_LS_RESPONSE = {
    "Name": EXAMPLE_BUCKET,
    "Prefix": "NBM/NBM/2026-04-29/",
    "Delimiter": "/",
    "CommonPrefixes": [
        {"Prefix": "NBM/NBM/2026-04-29/20260429_0100.zarr/"},
        {"Prefix": "NBM/NBM/2026-04-29/20260429_0700.zarr/"},
        {"Prefix": "NBM/NBM/2026-04-29/20260429_1300.zarr/"},
        {"Prefix": "NBM/NBM/2026-04-29/20260429_1900.zarr/"},
    ],
    "KeyCount": 4,
}


# fixtures
@fixture
def mock_datetime(monkeypatch: MonkeyPatch) -> Mock:
    mock_obj = Mock(name="mock_datetime", spec=datetime, now=Mock(return_value=EXAMPLE_NOW))
    monkeypatch.setattr("idsse.common.boto3_utils.datetime", mock_obj)
    return mock_obj


@fixture
def mock_sts() -> Mock:
    mock_obj = Mock(name="MockSts")
    mock_obj.get_caller_identity.return_value = CALLER_IDENTITY_RESPONSE
    mock_obj.assume_role.return_value = ASSUME_ROLE_RESPONSE
    return mock_obj


@fixture
def mock_boto3(monkeypatch: MonkeyPatch, mock_sts: Mock):
    mock_obj = Mock(name="mock_boto3", spec=boto3)
    mock_obj.client.return_value = mock_sts  # assume we only call .client('sts') in this class
    mock_obj.session = Mock(name="MockSession", spec=boto3.Session)

    monkeypatch.setattr("idsse.common.boto3_utils.boto3", mock_obj)
    return mock_obj


# @fixture
# def boto_utils() -> Boto3Utils:
#     return Boto3Utils(
#         basedir=f"s3://{EXAMPLE_BUCKET}/",
#         subdir="NBM/{issue.year:04d}-{issue.month:02d}-{issue.day:02d}/",
#         file_base=(
#             "{issue.year:04d}{issue.month:02d}{issue.day:02d}_{issue.hour:02d}{issue.minute:02d}"
#         ),
#         file_ext=".zarr",
#     )


# AwsSession tests
def test_aws_session(mock_boto3: Mock, mock_sts: Mock, mock_datetime: Mock):
    cache = AwsSession()

    result = cache.fetch_session()
    mock_sts.reset_mock()
    refetched_result = cache.fetch_session()

    assert result and result == refetched_result
    # only the first fetch() should've assumed role; second should have reused Session from memory
    mock_sts.assume_role.assert_not_called()


def test_session_expired(mock_boto3: Mock, mock_sts: Mock, mock_datetime: Mock):
    # pylint: disable=invalid-name
    def mock_assume_role(RoleArn, RoleSessionName, DurationSeconds=60 * 60):
        # simulate assume_role generating a new Expiration date in the future
        response = deepcopy(ASSUME_ROLE_RESPONSE)
        prev_expiration = response["Credentials"]["Expiration"]
        response["Credentials"]["Expiration"] = prev_expiration + timedelta(
            seconds=DurationSeconds
        )
        return response

    cache = AwsSession()
    # populate Session and simulate it becoming 5 minutes expired
    cache.fetch_session()
    mock_datetime.now.return_value = EXAMPLE_EXPIRATION + timedelta(minutes=5)
    mock_sts.reset_mock()

    assert cache.is_expired()

    mock_sts.assume_role.side_effect = mock_assume_role
    result = cache.fetch_session()

    assert result
    assert not cache.is_expired()
    # Session should have detected it was expired and refreshed itself
    mock_sts.assume_role.assert_called_once()


def test_session_client(mock_boto3: Mock, mock_datetime: Mock, mock_sts: Mock):
    cache = AwsSession()
    # populate Session and simulate it becoming 5 minutes expired
    cache.fetch_session()
    mock_datetime.now.return_value = EXAMPLE_EXPIRATION + timedelta(minutes=5)
    mock_sts.reset_mock()
    mock_boto3.reset_mock()

    cache.client("some_aws_service")

    mock_client_calls = [_call[1][0] for _call in mock_boto3.client.mock_calls]
    assert mock_client_calls == ["sts"]
    mock_boto3.Session.return_value.client.assert_called_once_with("some_aws_service")
    mock_sts.assume_role.assert_called_once()


def test_session_already_assumed(mock_boto3: Mock, mock_datetime: Mock, mock_sts: Mock):
    cache = AwsSession()

    assume_role_response = deepcopy(CALLER_IDENTITY_RESPONSE)
    assume_role_response["Arn"] = "arn:aws:iam::123456789012:assumed-role/my-role/i-0123292"
    mock_sts.get_caller_identity.return_value = assume_role_response

    result = cache.fetch_session()

    assert result
    # cannot call assume_role if we were already an assumed-role
    mock_sts.assume_role.assert_not_called()

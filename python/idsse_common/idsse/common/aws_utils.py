"""Helper function for listing directories and retrieving s3 objects"""

# -------------------------------------------------------------------------------
# Created on Tue Feb 14 2023
#
# Copyright (c) 2023 Colorado State University. All rights reserved. (1)
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (2)
#
# Contributors:
#     Geary Layne (2)
#     Paul Hamer (1)
#
# -------------------------------------------------------------------------------

import logging
import os
from collections.abc import Sequence

from .protocol_utils import ProtocolUtils
from .utils import exec_cmd

logger = logging.getLogger(__name__)


class AwsUtils(ProtocolUtils):
    """AWS Utility Class"""

    def ls(self, path: str, prepend_path: bool = True, **kwargs) -> Sequence[str]:
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

        try:
            commands = ["aws", "s3", "--no-sign-request", "ls", path]
            commands_result = exec_cmd(commands)
        except PermissionError:
            return []
        if prepend_path:
            return [os.path.join(path, filename.split(" ")[-1]) for filename in commands_result]
        return [filename.split(" ")[-1] for filename in commands_result]

    def cp(self, path: str, dest: str, **kwargs) -> bool:
        """Execute a 'cp' on the AWS s3 bucket specified by path, dest. Attempts to use
        aws-cli, which can be slow but works.

        Args:
            path (str): Relative or Absolute path to the object to be copied
            dest (str): The destination location

        Returns:
            bool: Returns True if copy is successful
        """
        try:
            logger.debug("Second attempt with aws command line")
            commands = ["aws", "s3", "--no-sign-request", "cp", path, dest]
            exec_cmd(commands)
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False
        finally:
            pass

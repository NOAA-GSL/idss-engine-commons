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

    def ls(self, path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the AWS s3 bucket specified by path

        Args:
            path (str): s3 bucket
            prepend_path (bool): Add to the filename

        Returns:
            Sequence[str]: The results sent to stdout from executing a 'ls' on passed path
        """
        return self.aws_ls(path, prepend_path)

    @staticmethod
    def aws_ls(path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the AWS s3 bucket specified by path

        Args:
            path (str): s3 bucket
            prepend_path (bool): Add to the filename

        Returns:
            Sequence[str]: The results sent to stdout from executing a 'ls' on passed path
        """
        try:
            commands = ['s5cmd',  '--no-sign-request', 'ls', path]
            commands_result = exec_cmd(commands)
        except FileNotFoundError:
            commands = ['aws', 's3',  '--no-sign-request', 'ls', path]
            commands_result = exec_cmd(commands)
        except PermissionError:
            return []
        if prepend_path:
            return [os.path.join(path, filename.split(' ')[-1]) for filename in commands_result]
        return [filename.split(' ')[-1] for filename in commands_result]

    @staticmethod
    def aws_cp(path: str,
               dest: str,
               concurrency: int | None = None,
               chunk_size: int | None = None) -> bool:
        """Execute a 'cp' on the AWS s3 bucket specified by path, dest. Attempts to use
        [s5cmd](https://github.com/peak/s5cmd) to copy the file from S3 with parallelization,
        but falls back to (slower) aws-cli if s5cmd is not installed or throws an error.

        Args:
            path (str): Relative or Absolute path to the object to be copied
            dest (str): The destination location
            concurrency (optional, int): Number of parallel threads for s5cmd to use to copy
                the file down from AWS (maybe helpful to tweak for large files).
                Default is None (s5cmd default).
            chunk_size (optional, int): Size of chunks (in MB) for s5cmd to split up the source AWS
                S3 file so it can download quicker with more threads.
                Default is None (s5cmd default).

        Returns:
            bool: Returns True if copy is successful
        """
        try:
            logger.debug('First attempt with s5cmd, concurrency: %d, chunk_size: %s',
                         concurrency, chunk_size)
            commands = ['s5cmd', '--no-sign-request',  'cp']

            # if concurrency and/or chunk_size options were provided, append to s5cmd before paths
            if concurrency:
                commands += ['--concurrency', str(concurrency)]
            if chunk_size:
                commands += ['--part-size', str(chunk_size)]
            commands += [path, dest]  # finish the command list with the src and destination

            exec_cmd(commands)
            return True
        except FileNotFoundError:
            try:
                logger.debug('Second attempt with aws command line')
                commands = ['aws', 's3', '--no-sign-request',  'cp', path, dest]
                exec_cmd(commands)
                return True
            except Exception:  # pylint: disable=broad-exception-caught
                return False
            finally:
                pass

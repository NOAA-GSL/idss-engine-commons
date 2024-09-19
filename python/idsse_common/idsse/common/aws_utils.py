"""Helper function for listing directories and retrieving s3 objects"""
# -------------------------------------------------------------------------------
# Created on Tue Feb 14 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# -------------------------------------------------------------------------------

import logging
import fnmatch
import os
from collections.abc import Sequence
from datetime import datetime, timedelta, UTC

from .path_builder import PathBuilder
from .utils import TimeDelta, datetime_gen, exec_cmd

logger = logging.getLogger(__name__)


class AwsUtils():
    """AWS Utility Class"""

    def __init__(self,
                 basedir: str,
                 subdir: str,
                 file_base: str,
                 file_ext: str) -> None:
        self.path_builder = PathBuilder(basedir, subdir, file_base, file_ext)

    def get_path(self, issue: datetime, valid: datetime) -> str:
        """Delegates to instant PathBuilder to get full path given issue and valid

        Args:
            issue (datetime): Issue date time
            valid (datetime): Valid date time

        Returns:
            str: Absolute path to file or object
        """
        lead = TimeDelta(valid-issue)
        return self.path_builder.build_path(issue=issue, valid=valid, lead=lead)

    def aws_ls(self, path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute an 'ls' on the AWS s3 bucket specified by path

        Args:
            path (str): s3 bucket

        Returns:
            Sequence[str]: The results sent to stdout from executing an 'ls' on passed path
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

    def aws_cp(self,
               path: str,
               dest: str,
               concurrency: int | None = None,
               chunk_size: int | None = None) -> bool:
        """Execute an 'cp' on the AWS s3 bucket specified by path, dest. Attempts to use
        [s5cmd](https://github.com/peak/s5cmd) to copy the file from S3 with parallelization,
        but falls back to (slower) aws-cli if s5cmd is not installed or throws an error.

        Args:
            path (str): Relative or Absolute path to the object to be copied
            dest (str): The destination location
            concurrency (optional, int): Number of parallel threads for s5cmd to use to copy
                the file down from AWS (may be helpful to tweak for large files).
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
                commands += ['--part_size', str(chunk_size)]
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

    def check_for(self, issue: datetime, valid: datetime) -> tuple[datetime, str] | None:
        """Checks if an object passed issue/valid exists

        Args:
            issue (datetime): The issue date/time used to format the path to the object's location
            valid (datetime): The valid date/time used to format the path to the object's location

        Returns:
            [tuple[datetime, str] | None]: A tuple of the valid date/time (indicated by object's
                                            location) and location (path) of a object, or None
                                            if object does not exist
        """
        lead = TimeDelta(valid-issue)
        file_path = self.get_path(issue, valid)
        dir_path = os.path.dirname(file_path)
        filenames = self.aws_ls(file_path, prepend_path=False)
        filename = self.path_builder.build_filename(issue=issue, valid=valid, lead=lead)
        for fname in filenames:
            # Support wildcard matches - used for '?' as a single wildcard character in
            # issue/valid time specs.
            if fnmatch.fnmatch(os.path.basename(fname), filename):
                return (valid, os.path.join(dir_path, fname))
        return None

    def get_issues(self,
                   num_issues: int = 1,
                   issue_start: datetime | None = None,
                   issue_end: datetime = datetime.now(UTC),
                   time_delta: timedelta = timedelta(hours=1)
                   ) -> Sequence[datetime]:
        """Determine the available issue date/times

        Args:
            num_issues (int): Maximum number of issue to return. Defaults to 1.
            issue_start (datetime, optional): The oldest date/time to look for. Defaults to None.
            issue_end (datetime): The newest date/time to look for. Defaults to now (UTC).
            time_delta (timedelta): The time step size. Defaults to 1 hour.

        Returns:
            Sequence[datetime]: A sequence of issue date/times
        """
        zero_time_delta = timedelta(seconds=0)
        if time_delta == zero_time_delta:
            raise ValueError('Time delta must be non zero')

        issues_set: set[datetime] = set()
        if issue_start:
            datetimes = datetime_gen(issue_end, time_delta, issue_start, num_issues)
        else:
            # check if time delta is positive, if so make negative
            if time_delta > zero_time_delta:
                time_delta = timedelta(seconds=-1.0 * time_delta.total_seconds())
            datetimes = datetime_gen(issue_end, time_delta)
        for issue_dt in datetimes:
            if issue_start and issue_dt < issue_start:
                break
            try:
                dir_path = self.path_builder.build_dir(issue=issue_dt)
                issues = {self.path_builder.get_issue(file_path)
                          for file_path in self.aws_ls(dir_path)
                          if file_path.endswith(self.path_builder.file_ext)}
                issues_set.update(issues)
                if num_issues and len(issues_set) >= num_issues:
                    break
            except PermissionError:
                pass
        return sorted(issues_set, reverse=True)[:num_issues]

    def get_valids(self,
                   issue: datetime,
                   valid_start: datetime | None = None,
                   valid_end: datetime | None = None) -> Sequence[tuple[datetime, str]]:
        """Get all objects consistent with the passed issue date/time and filter by valid range

        Args:
            issue (datetime): The issue date/time used to format the path to the object's location
            valid_start (datetime | None, optional): All returned objects will be for
                                              valids >= valid_start. Defaults to None.
            valid_end (datetime | None, optional): All returned objects will be for
                                            valids <= valid_end. Defaults to None.

        Returns:
            Sequence[tuple[datetime, str]]: A sequence of tuples with valid date/time (indicated by
                                            object's location) and the object's location (path).
                                            Empty Sequence if no valids found for given time range.
        """
        if valid_start and valid_start == valid_end:
            valids_and_filenames = self.check_for(issue, valid_start)
            return [valids_and_filenames] if valids_and_filenames is not None else []

        dir_path = self.path_builder.build_dir(issue=issue)
        valid_and_file = [(self.path_builder.get_valid(file_path), file_path)
                          for file_path in self.aws_ls(dir_path)
                          if file_path.endswith(self.path_builder.file_ext)]

        if valid_start:
            if valid_end:
                valid_and_file = [(valid, filename)
                                  for valid, filename in valid_and_file
                                  if valid_start <= valid <= valid_end]
            else:
                valid_and_file = [(valid, filename)
                                  for valid, filename in valid_and_file
                                  if valid >= valid_start]
        elif valid_end:
            valid_and_file = [(valid, filename)
                              for valid, filename in valid_and_file
                              if valid <= valid_end]

        return valid_and_file

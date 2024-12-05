"""Base class for http and awc data access"""
# -------------------------------------------------------------------------------
# Created on Tue Dec 3 2024
#
# Copyright (c) 2023 Colorado State University. All rights reserved.             (1)
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (2)
#
# Contributors:
#     Paul Hamer (1)
#
# -------------------------------------------------------------------------------
import fnmatch
import os

from abc import abstractmethod, ABC
from collections.abc import Sequence
from datetime import datetime, timedelta, UTC

from .path_builder import PathBuilder
from .utils import TimeDelta, datetime_gen

class ProtocolUtils(ABC):
    """Base Class - interface for DAS data discovery"""

    def __init__(self,
                 basedir: str,
                 subdir: str,
                 file_base: str,
                 file_ext: str) -> None:
        self.path_builder = PathBuilder(basedir, subdir, file_base, file_ext)

    # pylint: disable=invalid-name
    @abstractmethod
    def ls(self, path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the specified path

        Args:
            path (str): path
            prepend_path (bool): Add to the filename

        Returns:
            Sequence[str]: The results sent to stdout from executing a 'ls' on passed path
        """

    @abstractmethod
    def cp(self, path: str, dest: str) -> bool:
        """Execute download from path to dest.

        Args:
            path (str): The object to be copied
            dest (str): The destination location
        Returns:
            bool: Returns True if copy is successful
        """


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


    def check_for(self, issue: datetime, valid: datetime) -> tuple[datetime, str] | None:
        """Checks if an object passed issue/valid exists

        Args:
            issue (datetime): The issue date/time used to format the path to the object's location
            valid (datetime): The valid date/time used to format the path to the object's location

        Returns:
            [tuple[datetime, str] | None]: A tuple of the valid date/time (indicated by object's
                                            location) and location (path) of an object, or None
                                            if object does not exist
        """
        lead = TimeDelta(valid - issue)
        file_path = self.get_path(issue, valid)
        dir_path = os.path.dirname(file_path)
        filenames = self.ls(dir_path, prepend_path=False)
        filename = self.path_builder.build_filename(issue=issue, valid=valid, lead=lead)

        for fname in filenames:
            # Support wildcard matches - used for '?' as a single wildcard character in
            # issue/valid time specs.
            if fnmatch.fnmatch(os.path.basename(fname), filename):
                return valid, os.path.join(dir_path, fname)
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
                          for file_path in self.ls(dir_path)
                          if file_path.endswith(self.path_builder.file_ext)}
                issues_set.update(issues)
                if num_issues and len(issues_set) >= num_issues:
                    break
            except PermissionError:
                pass
        if None in issues_set:
            issues_set.remove(None)
        return sorted(issues_set)[:num_issues]

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
                          for file_path in self.ls(dir_path)
                          if file_path.endswith(self.path_builder.file_ext)]
        valid_and_file = [(dt, path) for (dt, path) in valid_and_file if dt is not None]
        # Remove any tuple that has "None" as the valid time
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

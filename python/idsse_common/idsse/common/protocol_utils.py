"""Base class for http and awc data access"""

# -------------------------------------------------------------------------------
# Created on Tue Dec 3 2024
#
# Copyright (c) 2024 Colorado State University. All rights reserved.             (1)
#
# Contributors:
#     Paul Hamer (1)
#     Mackenzie Grimes (1)
#
# -------------------------------------------------------------------------------
import fnmatch
import os

from abc import abstractmethod, ABC
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime, timedelta, UTC

from .path_builder import PathBuilder
from .utils import TimeDelta, datetime_gen


class ProtocolUtils(ABC):
    """Base Class - interface for DAS data discovery"""

    def __init__(self, basedir: str, subdir: str, file_base: str, file_ext: str) -> None:
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

    def get_path(self, issue: datetime, valid: datetime, **kwargs) -> str:
        """Delegates to instant PathBuilder to get full path given issue and valid

        Args:
            issue (datetime): Issue date time
            valid (datetime): Valid date time
            kwargs: Additional arguments, e.g. region

        Returns:
            str: Absolute path to file or object
        """
        lead = TimeDelta(valid - issue)
        return self.path_builder.build_path(issue=issue, valid=valid, lead=lead, **kwargs)

    def check_for(self, issue: datetime, valid: datetime, **kwargs) -> tuple[datetime, str] | None:
        """Checks if an object passed issue/valid exists

        Args:
            issue (datetime): The issue date/time used to format the path to the object's location
            valid (datetime): The valid date/time used to format the path to the object's location
            kwargs: Additional arguments, e.g. region

        Returns:
            [tuple[datetime, str] | None]: A tuple of the valid date/time (indicated by object's
                                            location) and location (path) of an object, or None
                                            if object does not exist
        """
        lead = TimeDelta(valid - issue)
        file_path = self.get_path(issue, valid)
        dir_path = os.path.dirname(file_path)
        filenames = self.ls(dir_path, prepend_path=False)
        filename = self.path_builder.build_filename(issue=issue, valid=valid, lead=lead, **kwargs)

        for fname in filenames:
            # Support wildcard matches - used for '?' as a single wildcard character in
            # issue/valid time specs.
            if fnmatch.fnmatch(os.path.basename(fname), filename):
                return valid, os.path.join(dir_path, fname)
        return None

    # pylint: disable=too-many-arguments
    def get_issues(
        self,
        num_issues: int | None = 1,
        issue_start: datetime | None = None,
        issue_end: datetime | None = None,
        time_delta: timedelta = timedelta(hours=1),
        max_workers: int = 24,
        **kwargs,
    ) -> Sequence[datetime]:
        """Determine the available issue date/times

        Args:
            num_issues (int): Maximum number of issue to return. Defaults to 1.
            issue_start (datetime, optional): The oldest date/time to look for. Defaults to None.
            issue_end (datetime): The newest date/time to look for. Defaults to now (UTC).
            time_delta (timedelta): The time step size. Defaults to 1 hour.
            max_workers (int): The number of Python threads to use to make server ls() calls.
                Defaults to 24, which is reasonable. More threads will not necessarily run faster.
            kwargs: Additional arguments, e.g. region

        Returns:
            Sequence[datetime]: A sequence of issue date/times
        """
        zero_time_delta = timedelta(seconds=0)
        if time_delta == zero_time_delta:
            raise ValueError("Time delta must be non zero")

        if not issue_end:
            issue_end = datetime.now(UTC)
        if issue_start:
            datetimes = list(datetime_gen(issue_end, time_delta, issue_start, num_issues))
        else:
            # check if time delta is positive, if so make negative
            if time_delta > zero_time_delta:
                time_delta = timedelta(seconds=-1.0 * time_delta.total_seconds())
            datetimes = list(datetime_gen(issue_end, time_delta))

        # build list of filepaths on the server for each dt (ignoring ones earlier than issue_dt)
        issue_filepaths = [
            self.path_builder.build_dir(issue=dt, **kwargs)
            for dt in datetimes
            if not (issue_start and dt < issue_start)
        ]

        issues_with_valid_dts = self._get_unique_issues(issue_filepaths, num_issues, max_workers)
        return sorted(list(issues_with_valid_dts))[:num_issues]

    def get_valids(
        self,
        issue: datetime,
        valid_start: datetime | None = None,
        valid_end: datetime | None = None,
        **kwargs,
    ) -> Sequence[tuple[datetime, str]]:
        """Get all objects consistent with the passed issue date/time and filter by valid range

        Args:
            issue (datetime): The issue date/time used to format the path to the object's location
            valid_start (datetime | None, optional): All returned objects will be for
                                              valids >= valid_start. Defaults to None.
            valid_end (datetime | None, optional): All returned objects will be for
                                            valids <= valid_end. Defaults to None.
            kwargs: Additional arguments, e.g. region

        Returns:
            Sequence[tuple[datetime, str]]: A sequence of tuples with valid date/time (indicated by
                                            object's location) and the object's location (path).
                                            Empty Sequence if no valids found for given time range.
        """
        if valid_start and valid_start == valid_end:
            valids_and_filenames = self.check_for(issue, valid_start)
            return [valids_and_filenames] if valids_and_filenames is not None else []

        dir_path = self.path_builder.build_dir(issue=issue, **kwargs)
        valid_and_file = []
        for file_path in self.ls(dir_path):
            if file_path.endswith(self.path_builder.file_ext):
                try:
                    if issue == self.path_builder.get_issue(file_path):
                        valid_and_file.append((self.path_builder.get_valid(file_path), file_path))
                except ValueError:  # Ignore invalid filepaths...
                    pass
        valid_and_file = [(dt, path) for (dt, path) in valid_and_file if dt is not None]
        # Remove any tuple that has "None" as the valid time
        if valid_start:
            if valid_end:
                valid_and_file = [
                    (valid, filename)
                    for valid, filename in valid_and_file
                    if valid_start <= valid <= valid_end
                ]
            else:
                valid_and_file = [
                    (valid, filename) for valid, filename in valid_and_file if valid >= valid_start
                ]
        elif valid_end:
            valid_and_file = [
                (valid, filename) for valid, filename in valid_and_file if valid <= valid_end
            ]

        return valid_and_file

    def _get_unique_issues(
        self,
        dir_paths: list[str],
        num_issues: int,
        max_workers: int,
    ) -> list[datetime]:
        """
        Based on a list of server directory paths, find all issue_dts on the server
        that seem ready (have valid_dt files). Server network calls will be made in parallel,
        up to `max_workers` number of threads at a time.

        Returns:
            list[datetime]: A list of unique issue_dts confirmed to be ready on the server
        """
        ready_issues: set[datetime] = set()
        paths_to_request = dir_paths  # create local copy, because we're going to mutate

        target_num_issues = num_issues if num_issues else len(paths_to_request)
        # if caller only asked for 1, 2, 6, etc. issue_dts, we don't need to use 24 threads
        thread_count = min(max_workers, target_num_issues)

        with ThreadPoolExecutor(thread_count, "AwsLsThread") as pool:
            # we have to use this while-loop approach, rather than just slicing the `datetimes`
            # above to the number of requested `num_issues`, because we can't know how many
            # non-empty filepaths we will find on the server until we try
            while len(ready_issues) < target_num_issues and len(paths_to_request) > 0:
                # list.pop() the next few filepaths (removing them from the overall filepaths list)
                filepaths_chunk = paths_to_request[:thread_count]
                paths_to_request = paths_to_request[thread_count:]
                futures = [
                    pool.submit(self._get_issue, dir_path, num_issues)
                    for dir_path in filepaths_chunk
                ]

                wait(futures)  # run the `ls` on all these server directories in parallel
                for future in futures:
                    try:
                        issues_in_aws = future.result()
                        ready_issues.update(issues_in_aws)
                    except PermissionError:
                        pass  # no valid_dt was available on server for this issue_dt yet; ignore

        return list(ready_issues)

    def _get_issue(self, dir_path: str, num_issues: int = 1) -> list[datetime]:
        """Get all objects consistent with the passed directory path and filter by valid range

        Args:
            dir_path (str): The directory path

        Returns:
            Sequence[tuple[datetime, str]]: A sequence of tuples with valid date/time (indicated by
                                            object's location) and the object's location (path).
                                            Empty Sequence if no valids found for given time range.
        """
        issues_set: set[datetime] = set()
        # sort files alphabetically in reverse; this should give us the longest lead time first
        # which is more indicative that the issueDt is fully available on this server
        valid_filepaths_in_dir = sorted(
            (f for f in self.ls(dir_path) if f.endswith(self.path_builder.file_ext)), reverse=True
        )

        for valid_file_path in valid_filepaths_in_dir:
            try:
                if issue_dt := self.path_builder.get_issue(valid_file_path):
                    issues_set.add(issue_dt)
            except ValueError:  # Ignore invalid filepaths...
                pass
        return sorted(list(issues_set), reverse=True)[:num_issues]

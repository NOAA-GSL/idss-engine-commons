"""Helper function for listing directories and retrieving s3 objects"""
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
import logging
import os
import shutil
from collections.abc import Sequence
from datetime import datetime, timedelta, UTC

import requests

from .protocol_utils import ProtocolUtils

logger = logging.getLogger(__name__)

# pylint: disable=duplicate-code, broad-exception-caught

class HttpUtils(ProtocolUtils):
    """http Utility Class - Used by DAS for file downloads"""
    def __init__(self,
                 basedir: str,
                 subdir: str,
                 file_base: str,
                 file_ext: str) -> None:
        super().__init__(basedir, subdir, file_base, file_ext)

    def get_path(self, issue: datetime, valid: datetime) -> str:
        """Delegates to instant PathBuilder to get full path given issue and valid

        Args:
            issue (datetime): Issue date time
            valid (datetime): Valid date time

        Returns:
            str: Absolute path to file or object
        """
        return super().get_path(issue, valid)

    def ls(self, path: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the AWS s3 bucket specified by path

        Args:
            path (str): s3 bucket
            prepend_path (bool): Add to the filename

        Returns:
            Sequence[str]: The results sent to stdout from executing a 'ls' on passed path
        """
        return self.http_ls(path, prepend_path)


    @staticmethod
    def http_ls(url: str, prepend_path: bool = True) -> Sequence[str]:
        """Execute a 'ls' on the http(s) server
        Args:
            url (str): URL
            prepend_path (bool): Add URL+ to the filename
        Returns:
            Sequence[str]: The results from executing a request get on passed url
        """
        try:
            files = []
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes

            for line in response.text.splitlines():
                if 'href="' in line:
                    filename = line.split('href="')[1].split('"')[0]
                    if not filename.endswith('/'):  # Exclude directories
                        files.append(filename)

        except requests.exceptions.RequestException as exp:
            logger.warning('Unable to query supplied URL: %s', str(exp))
            return []
        if prepend_path:
            return [os.path.join(url, filename) for filename in files]
        return files

    @staticmethod
    def http_cp(url: str, dest: str) -> bool:
        """Execute http request download from URL to dest.

        Args:
            url (str): URL to the object to be copied
            dest (str): The destination location
        Returns:
            bool: Returns True if copy is successful
        """
        try:
            with requests.get(os.path.join(url), timeout=5, stream=True) as response:
                # Check if the request was successful
                if response.status_code == 200:
                    # Open a file in binary write mode
                    with open(dest, "wb") as file:
                        shutil.copyfileobj(response.raw, file)
                    return True

                logger.debug('copy fail: request status code: %s', response.status_code)
                return False
        except Exception:  # pylint: disable=broad-exception-caught
            return False

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
        return super().check_for(issue, valid)

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
        return super().get_issues(num_issues, issue_start, issue_end, time_delta)

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
        return super().get_valids(issue, valid_start, valid_end)
"""Module for building (and parsing) paths that are dependent on issue, valid, and lead"""
# -------------------------------------------------------------------------------
# Created on Thu Feb 16 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# -------------------------------------------------------------------------------

import os
import re
from datetime import datetime, timedelta
from typing import Dict, Self, Tuple, Union

from .utils import TimeDelta


class PathBuilder():
    """Path Builder Class"""

    def __init__(self,
                 basedir: str,
                 subdir: str,
                 file_base: str,
                 file_ext: str) -> None:
        self._basedir = basedir
        self._subdir = subdir
        self._file_base = file_base
        self._file_ext = file_ext

    def __str__(self) -> str:
        return f"'{self._basedir}','{self._subdir}','{self._file_base}','{self._file_ext}'"

    def __repr__(self) -> str:
        return (f"PathBuilder(basedir='{self._basedir}', subdir='{self._subdir}', "
                f"file_base='{self._file_base}', file_ext='{self._file_ext}')")

    @classmethod
    def from_dir_filename(cls, dir_fmt: str, filename_fmt: str) -> Self:
        """Construct a PathBuilder object from specified directory and filename formats

        Args:
            dir_fmt (str): Format string for the directory
            filename_fmt (str): Format string for the filename

        Returns:
            Self: The newly created PathBuilder object
        """
        return PathBuilder(dir_fmt, '', filename_fmt, '')

    @classmethod
    def from_path(cls, path_fmt: str) -> Self:
        """Construct a PathBuilder object from specified path formats

        Args:
            path_fmt (str): Format string for the path, should contain both directory and filename

        Returns:
            Self: The newly created PathBuilder object
        """
        idx = path_fmt.rindex(os.path.sep)
        return PathBuilder(path_fmt[:idx], '', path_fmt[:idx], '')

    @property
    def dir_fmt(self):
        """Provides access to the directory format str"""
        return os.path.join(self._basedir, self._subdir)

    @property
    def filename_fmt(self):
        """Provides access to the filename format str"""
        if not self._file_ext or self._file_ext.startswith('.'):
            return f'{self._file_base}{self._file_ext}'
        return f'{self._file_base}.{self._file_ext}'

    @property
    def file_ext(self):
        """Provides access to the file extension format str"""
        if self._file_ext:
            return self._file_ext
        return self._file_base[self._file_base.rindex('.'):]

    @file_ext.setter
    def file_ext(self, ext):
        """Set the file extension format str"""
        self._file_ext = ext

    @property
    def path_fmt(self):
        """Provides access to the path format str"""
        return os.path.join(self.dir_fmt, self.filename_fmt)

    def build_dir(self,
                  issue: datetime = None,
                  valid: datetime = None,
                  lead: Union[timedelta, TimeDelta] = None) -> str:
        """Attempts to build the directory with provided arguments

        Args:
            issue (datetime, optional): Issue datetime, should be provided is the
                                        directory is dependant on it. Defaults to None.
            valid (datetime, optional): Valid datetime, should be provided is the
                                        directory is dependant on it. . Defaults to None.
            lead (Union[timedelta, TimeDelta], optional): Lead can be provided in addition
                                                          to issue or valid. Defaults to None.

        Returns:
            str: Directory as a string
        """
        if issue is None:
            return None
        lead = self._insure_lead(issue, valid, lead)
        return self.dir_fmt.format(issue=issue, valid=valid, lead=lead)

    def build_filename(self,
                       issue: datetime = None,
                       valid: datetime = None,
                       lead: Union[timedelta, TimeDelta] = None) -> str:
        """Attempts to build the filename with provided arguments

        Args:
            issue (datetime, optional): Issue datetime, should be provided is the
                                        filename is dependant on it. Defaults to None.
            valid (datetime, optional): Valid datetime, should be provided is the
                                        filename is dependant on it. . Defaults to None.
            lead (Union[timedelta, TimeDelta], optional): Lead can be provided in addition
                                                          to issue or valid. Defaults to None.

        Returns:
            str: File name as a string
        """
        lead = self._insure_lead(issue, valid, lead)
        return self.filename_fmt.format(issue=issue, valid=valid, lead=lead)

    def build_path(self,
                   issue: datetime = None,
                   valid: datetime = None,
                   lead: Union[timedelta, TimeDelta] = None) -> str:
        """Attempts to build the path with provided arguments

        Args:
            issue (datetime, optional): Issue datetime, should be provided is the
                                        path is dependant on it. Defaults to None.
            valid (datetime, optional): Valid datetime, should be provided is the
                                        path is dependant on it. . Defaults to None.
            lead (Union[timedelta, TimeDelta], optional): Lead can be provided in addition
                                                          to issue or valid. Defaults to None.

        Returns:
            str: Path as a string
        """
        lead = self._insure_lead(issue, valid, lead)
        return self.path_fmt.format(issue=issue, valid=valid, lead=lead)

    def parse_dir(self, dir_: str) -> dict:
        """Extracts issue, valid, and/or lead information from the provided directory

        Args:
            dir_ (str): A directory consistent with this PathBuilder

        Returns:
            dict: Lookup of all information identified and extracted
        """
        return self._parse(dir_, self.dir_fmt)

    def parse_filename(self, filename: str) -> dict:
        """Extracts issue, valid, and/or lead information from the provided filename

        Args:
            dir_ (str): A filename consistent with this PathBuilder

        Returns:
            dict: Lookup of all information identified and extracted
        """
        return self._parse(filename, self.filename_fmt)

    def parse_path(self, path: str) -> dict:
        """Extracts issue, valid, and/or lead information from the provided path

        Args:
            dir_ (str): A path consistent with this PathBuilder

        Returns:
            dict: Lookup of all information identified and extracted
        """
        return self._parse(path, self.path_fmt)

    def get_issue(self, path: str) -> datetime:
        """Retrieves the issue date/time from the provided path

        Args:
            path (str): A path consistent with this PathBuilder

        Returns:
            datetime: After parsing the path, builds and returns the issue date/time
        """
        time_args = self.parse_path(path)
        return self.get_issue_from_time_args(time_args)

    def get_valid(self, path: str) -> datetime:
        """Retrieves the valid date/time from the provided path

        Args:
            path (str): A path consistent with this PathBuilder

        Returns:
            datetime: After parsing the path, builds and returns the valid date/time
        """
        time_args = self.parse_path(path)
        return self.get_valid_from_time_args(time_args)

    @staticmethod
    def get_issue_from_time_args(parsed_args: Dict,
                                 valid: datetime = None,
                                 lead: timedelta = None) -> datetime:
        """Static method for creating an issue date/time from parsed arguments and optional inputs

        Args:
            parsed_args (dict): A dictionary of issue, valid and/or lead info resulting from parsing
                                a path, dir, or filename
            valid (datetime, optional): Depending on info found during parsing, valid date/time
                                        can be useful. Defaults to None.
            lead (timedelta, optional): Depending on info found during parsing, lead time
                                        can be useful. . Defaults to None.

        Returns:
            datetime: Issue date/time
        """
        if 'issue.year' in parsed_args:
            return datetime(parsed_args.get('issue.year'),
                            parsed_args.get('issue.month'),
                            parsed_args.get('issue.day'),
                            parsed_args.get('issue.hour', 0),
                            parsed_args.get('issue.minute', 0),
                            parsed_args.get('issue.second', 0),
                            parsed_args.get('issue.microsecond', 0))

        if lead is None:
            lead = PathBuilder.get_lead_from_time_args(parsed_args)

        if valid is None and 'valid.year' in parsed_args:
            valid = PathBuilder.get_valid_from_time_args(parsed_args)

        if valid and lead:
            return valid - lead

    @staticmethod
    def get_valid_from_time_args(parsed_args: dict,
                                 issue: datetime = None,
                                 lead: timedelta = None) -> datetime:
        """Static method for creating an valid date/time from parsed arguments and optional inputs

        Args:
            parsed_args (dict): A dictionary of issue, valid and/or lead info resulting from parsing
                                a path, dir, or filename
            issue (datetime, optional): Depending on info found during parsing, issue date/time
                                        can be useful. Defaults to None.
            lead (timedelta, optional): Depending on info found during parsing, lead time
                                        can be useful. . Defaults to None.

        Returns:
            datetime: Valid date/time
        """
        if 'valid.year' in parsed_args:
            return datetime(parsed_args.get('valid.year'),
                            parsed_args.get('valid.month'),
                            parsed_args.get('valid.day'),
                            parsed_args.get('valid.hour', 0),
                            parsed_args.get('valid.minute', 0),
                            parsed_args.get('valid.second', 0),
                            parsed_args.get('valid.microsecond', 0))

        if lead is None:
            lead = PathBuilder.get_lead_from_time_args(parsed_args)

        if issue is None and 'issue.year' in parsed_args:
            issue = PathBuilder.get_issue_from_time_args(parsed_args)

        if issue and lead:
            return issue + lead

        return None

    @staticmethod
    def get_lead_from_time_args(time_args: dict) -> timedelta:
        """Static method for creating an lead time from parsed arguments and optional inputs

        Args:
            parsed_args (dict): A dictionary of issue, valid and/or lead info resulting from parsing
                                a path, dir, or filename
            issue (datetime, optional): Depending on info found during parsing, issue date/time
                                        can be useful. Defaults to None.
            valid (datetime, optional): Depending on info found during parsing, valid date/time
                                        can be useful. Defaults to None.

        Returns:
            timedelta: Lead time
        """
        return timedelta(hours=time_args['lead.hour'])

    @staticmethod
    def _insure_lead(issue: datetime,
                     valid: datetime,
                     lead: Union[timedelta, TimeDelta]) -> TimeDelta:
        if lead:
            if isinstance(lead, timedelta):
                return TimeDelta(lead)
            return lead
        if issue and valid:
            return TimeDelta(valid-issue)
        return None

    def _parse(self, string: str, format_str: str) -> Dict:
        def get_between(string: str, pre: str, post: str) -> Tuple[str, str]:
            idx1 = string.index(pre) + len(pre)
            idx2 = string.index(post, idx1)
            return (string[idx1:idx2], string[idx2:])

        def parse_args(key: str, value: str, result: Dict):
            for arg in key.split('{')[1:]:
                var_name, var_size = arg.split(':')
                var_type = var_size[-2:-1]
                var_size = int(var_size[:-2])
                match var_type:
                    case 'd':
                        result[var_name] = int(value[:var_size])
                    case _:
                        raise ValueError(f'Unknown format type: {var_type}')
                key = key[var_size:]
                value = value[var_size:]

        constants = [part for part in re.split(r'{.*?}', format_str) if part]

        arg_lookup = {}
        for i in range(1, len(constants)):
            pre = constants[i-1]
            post = constants[i]
            format_between, format_str = get_between(format_str, pre, post)
            string_between, string = get_between(string, pre, post)
            arg_lookup[format_between] = string_between

        time_args = {}
        for k, v in arg_lookup.items():
            parse_args(k, v, time_args)

        return time_args


def _test():
    basedir = 's3://noaa-nbm-grib2-pds/'
    subdir = 'blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/core/'
    file_base = 'blend.t{issue.hour:02d}z.core.f{lead.hour:03d}.co'
    file_ext = '.grib2.idx'

    # pb = PathBuilder(basedir=basedir, subdir=subdir, file_base=file_base, file_ext=file_ext)
    pb = PathBuilder.from_dir_filename(basedir+subdir, file_base+file_ext)

    path = 's3://noaa-nbm-grib2-pds/blend.20230211/14/core/blend.t14z.core.f011.co.grib2.idx'

    logging.info(pb)
    logging.info('valid', pb.get_valid(path))


if __name__ == '__main__':
    import logging
    _test()
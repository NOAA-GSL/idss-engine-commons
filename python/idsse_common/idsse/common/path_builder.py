"""Module for building (and parsing) paths that are dependent on issue, valid, and lead.

In this weather forecasting data context,
- issue: the datetime when a given forecast was generated (or at least when generation began)
- valid: the datetime when a given forecast "expires" or is superseded by newer forecasts
- lead: the time duration (often in hours) between issue and valid
"""

# ----------------------------------------------------------------------------------
# Created on Thu Feb 16 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2025 Colorado State University. All rights reserved.             (2)
#
# Contributors:
#     Geary J Layne     (1)
#     Mackenzie Grimes  (2)
#
# ----------------------------------------------------------------------------------

import os
import re
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from typing import Final, NamedTuple, Self

from .utils import TimeDelta


# The public class
class PathBuilder:
    """Path Builder Class"""

    ISSUE: Final[str] = "issue"
    VALID: Final[str] = "valid"
    LEAD: Final[str] = "lead"
    LEAFDIR: Final[str] = "leafdir"
    INT: Final[str] = "d"
    FLOAT: Final[str] = "f"
    STR: Final[str] = "s"

    def __init__(self, basedir: str, subdir: str, file_base: str, file_ext: str) -> None:

        # store path format parts to private vars, they accessible via properties
        self._base_dir = basedir
        self._sub_dir = subdir
        self._file_base = file_base
        self._file_ext = file_ext

        # create a dictionary to hold lookup info
        self._lookup_dict = {}
        self._update_lookup(self.path_fmt)

        # these are used for caching the most recent previously parsed paths (for optimization)
        self._last_parsed_path = None
        self._parsed_args = None

    def __str__(self) -> str:
        return f"'{self._base_dir}','{self._sub_dir}','{self._file_base}','{self._file_ext}'"

    def __repr__(self) -> str:
        return (
            f"PathBuilder(basedir='{self._base_dir}', subdir='{self._sub_dir}', "
            f"file_base='{self._file_base}', file_ext='{self._file_ext}')"
        )

    @classmethod
    def from_dir_filename(cls, dir_fmt: str, filename_fmt: str) -> Self:
        """Construct a PathBuilder object from specified directory and filename formats.
        Format string args must follow Python format specifications to define expected fields:
        https://docs.python.org/3/library/string.html#format-specification-mini-language

        For example, filepaths could be expected to contain "issue" and "lead" fields using format:
        'blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/{lead.hour:03d}/'

        Args:
            dir_fmt (str): Python format string for the directory
            filename_fmt (str): Python format string for the filename

        Returns:
            Self: The newly created PathBuilder object
        """
        return PathBuilder(dir_fmt, "", filename_fmt, "")

    @classmethod
    def from_path(cls, path_fmt: str) -> Self:
        """Construct a PathBuilder object from specified path formats

        Args:
            path_fmt (str): Format string for the path, should contain both directory and filename

        Returns:
            Self: The newly created PathBuilder object
        """
        idx = path_fmt.rindex(os.path.sep)
        return PathBuilder(path_fmt[:idx], "", path_fmt[idx + 1 :], "")

    @property
    def dir_fmt(self):
        """Provides access to the directory format string"""
        return os.path.join(self.base_dir, self.sub_dir)

    @property
    def filename_fmt(self):
        """Provides access to the filename format string"""
        if not self.file_ext or self.file_ext.startswith("."):
            return f"{self.file_base}{self.file_ext}"
        return f"{self.file_base}.{self.file_ext}"

    @property
    def path_fmt(self):
        """Provides access to the path format string"""
        return os.path.join(self.dir_fmt, self.filename_fmt)

    @property
    def base_dir(self):
        """Provides access to the file base directory format string"""
        return self._base_dir

    @base_dir.setter
    def base_dir(self, basedir):
        """Set the base directory format string"""
        # update base directory format
        self._base_dir = basedir
        self._update_lookup(self.path_fmt)

    @property
    def sub_dir(self) -> str:
        """Provides access to the file base directory format string"""
        return self._sub_dir

    @sub_dir.setter
    def sub_dir(self, subdir: str):
        """Set the sub directory format string"""
        # update sub directory format
        self._sub_dir = subdir
        self._update_lookup(self.path_fmt)

    @property
    def file_base(self):
        """Provides access to the file base format string"""
        return self._file_base

    @file_base.setter
    def file_base(self, file_base):
        """Set the file extension format string"""
        # update file extension format
        self._file_base = file_base
        self._update_lookup(self.path_fmt)

    @property
    def file_ext(self):
        """Provides access to the file extension format string"""
        if self._file_ext:
            return self._file_ext
        return self._file_base[self._file_base.rindex(".") :]

    @file_ext.setter
    def file_ext(self, ext):
        """Set the file extension format string"""
        # update file extension format
        self._file_ext = ext
        self._update_lookup(self.path_fmt)

    def build_dir(
        self,
        issue: datetime | None = None,
        valid: datetime | None = None,
        lead: timedelta | TimeDelta | None = None,
        leafdir: str | None = None,
        **kwargs,
    ) -> str:
        """Attempts to build the directory with provided arguments

        Args:
            issue (datetime | None, optional): Issue datetime, should be provided is the
                                        directory is dependant on it. Defaults to None.
            valid (datetime | None, optional): Valid datetime, should be provided is the
                                        directory is dependant on it. . Defaults to None.
            lead (timedelta | TimeDelta | None, optional): Lead can be provided in addition
                                                          to issue or valid. Defaults to None.
            leafdir (str | None, optional): Name of last directory in subdirectory path, if this
                Path Builder's `subdir` fmt str supports multiple subdirectories. Defaults to None.
            **kwargs: Any additional key/word args (i.e. 'region'='co')

        Returns:
            str: Directory as a string
        """
        if issue is None:
            return None
        lead = self._ensure_lead(issue, valid, lead)
        return self.dir_fmt.format(issue=issue, valid=valid, lead=lead, leafdir=leafdir, **kwargs)

    def build_filename(
        self,
        issue: datetime | None = None,
        valid: datetime | None = None,
        lead: timedelta | TimeDelta | None = None,
        leafdir: str | None = None,
        **kwargs,
    ) -> str:
        """Attempts to build the filename with provided arguments

        Args:
            issue (datetime | None, optional): Issue datetime, should be provided is the
                                        filename is dependant on it. Defaults to None.
            valid (datetime | None, optional): Valid datetime, should be provided is the
                                        filename is dependant on it. . Defaults to None.
            lead (timedelta | TimeDelta | None, optional): Lead can be provided in addition
                                                          to issue or valid. Defaults to None.
            leafdir (str | None, optional): Name of last directory in subdirectory path, if this
                Path Builder's `subdir` fmt str supports multiple subdirectories. Defaults to None.
            **kwargs: Any additional key/word args (i.e. 'region'='co')

        Returns:
            str: File name as a string
        """
        lead = self._ensure_lead(issue, valid, lead)
        return self.filename_fmt.format(
            issue=issue, valid=valid, lead=lead, leafdir=leafdir, **kwargs
        )

    def build_path(
        self,
        issue: datetime | None = None,
        valid: datetime | None = None,
        lead: timedelta | TimeDelta | None = None,
        leafdir: str | None = None,
        **kwargs: dict,
    ) -> str:
        """Attempts to build the path with provided arguments

        Args:
            issue (datetime | None, optional): Issue datetime, should be provided is the
                path is dependant on it. Defaults to None.
            valid (datetime | None, optional): Valid datetime, should be provided is the
                path is dependant on it. Defaults to None.
            lead (timedelta | TimeDelta | None, optional): Lead can be provided in addition
                to issue or valid. Defaults to None.
            leafdir (str | None, optional): the last directory in the subdirectory path, e.g.
                "core" or "qmd". Not needed if this PathBuilder's format string `subdir` contains
                no `{leafdir}` argument. Defaults to None.
            **kwargs: Any additional key/word args (i.e. 'region'='co')

        Returns:
            str: Path as a string
        """
        lead = self._ensure_lead(issue, valid, lead)
        return self._apply_format(
            self.path_fmt, issue=issue, valid=valid, lead=lead, leafdir=leafdir, **kwargs
        )

    def parse_dir(self, dir_str: str) -> dict:
        """Extracts issue, valid, and/or lead information from the provided directory

        Args:
            dir_str (str): A directory consistent with this PathBuilder

        Returns:
            dict: Lookup of all information identified and extracted
        """
        return self._get_parsed_arg_parts(dir_str, self.dir_fmt)

    def parse_filename(self, filename: str) -> dict:
        """Extracts issue, valid, lead, and any extras information from the provided filename

        Args:
            filename (str): A filename consistent with this PathBuilder

        Returns:
            dict: Lookup of all information identified and extracted
        """
        filename = os.path.basename(filename)
        self._parse_path(filename, self.filename_fmt)
        return deepcopy(self._parsed_args)

    def parse_path(self, path: str) -> dict:
        """Extracts issue, valid, lead, and any extra information from the provided path

        Args:
            path (str): A path consistent with this PathBuilder

        Returns:
            dict: Lookup of all information identified and extracted
        """
        # do the core parsing
        self._parse_path(path, self.path_fmt)
        # return a copy to parsed_args
        return deepcopy(self._parsed_args)

    def get_issue(self, path: str) -> datetime | None:
        """Retrieves the issue date/time from the provided path

        Args:
            path (str): A path consistent with this PathBuilder

        Returns:
            datetime | None: After parsing the path, builds and returns the issue date/time if
                             possible else returns None if insufficient info is available to build
        """
        # do the core parsing
        self._parse_path(path, self.path_fmt)
        # return a the issue datetime, if determined
        return self._parsed_args.get(self.ISSUE, None)

    def get_valid(self, path: str) -> datetime | None:
        """Retrieves the valid date/time from the provided path

        Args:
            path (str): A path consistent with this PathBuilder

        Returns:
            str | None: After parsing the path, builds and returns the valid date/time if
                             possible else returns None if insufficient info is available to build
        """
        # do the core parsing
        self._parse_path(path, self.path_fmt)
        # return a the valid datetime, if determined
        return self._parsed_args.get(self.VALID, None)

    def get_leafdir(self, path: str) -> str | None:
        """Retrieves the leafdir (last directory in subdir) from the provided path

        Args:
            path (str): A path consistent with this PathBuilder

        Returns:
            str | None: After parsing the path, returns the leafdir (str), else returns None
                if insufficient info is available to build.
        """
        # do the core parsing
        self._parse_path(path, self.path_fmt)
        return self._parsed_args.get(self.LEAFDIR, None)

    def _update_lookup(self, fmt_str: str) -> None:
        """This method should be called whenever some part of the format has been changed.

        Args:
            fmt_str (str): The change format, either part of, or the complete combined, format

        Raises:
            ValueError: If the format is not descriptive enough. Formats must specify size and type.
        """
        # if a format is being updated any cache will be out of date
        self._last_parsed_path = None

        for fmt_part in os.path.normpath(fmt_str).split(os.sep):
            remaining_fmt_part = fmt_part
            lookup_info = []
            cum_start = 0
            while re_match := re.search(r"\{(.*?)\}", remaining_fmt_part):
                arg_parts = re_match.group()[1:-1].split(":")
                if len(arg_parts) != 2:
                    raise ValueError(
                        'Format string must have explicit specification (must include a ":")'
                    )
                try:
                    arg_size = int(re.search(r"^\d+", arg_parts[1]).group())
                except Exception:
                    # pylint: disable=raise-missing-from
                    raise ValueError(
                        'Format string must have explicit size (must include a number after ":")'
                    )
                arg_type = arg_parts[1][-1]
                if arg_parts[1][-1] not in [self.INT, self.FLOAT, self.STR]:
                    raise ValueError(
                        "Format string must have explicit type (must include one of "
                        f'["{self.INT}", "{self.FLOAT}", "{self.STR}"] after ":")'
                    )

                arg_start = re_match.start() + cum_start
                arg_end = cum_start = arg_start + arg_size
                lookup_info.append(_LookupInfo(arg_parts[0], arg_start, arg_end, arg_type))
                # update the format str to find the next argument
                remaining_fmt_part = remaining_fmt_part[re_match.end() :]

            exp_len = sum(end - start for _, start, end, _ in lookup_info) + len(
                re.sub(r"\{(.*?)\}", "", fmt_part)
            )

            self._lookup_dict[fmt_part] = _FormatLookup(exp_len, lookup_info)
        # add default for empty string
        self._lookup_dict[""] = _FormatLookup(0, [])

    def _parse_path(self, path: str, fmt_str: str) -> None:
        """Parse a path for any knowable variables given the provided format string.

        Args:
            path (str): The path string to be parsed
            fmt_str (str): The format string that the path is assumed to correspond with
        """
        if path != self._last_parsed_path:
            parsed_arg_parts = self._get_parsed_arg_parts(path, fmt_str)
            issue_dt = self._get_issue_from_arg_parts(parsed_arg_parts)
            valid_dt = self._get_valid_from_arg_parts(parsed_arg_parts)
            # add the issue/valid/lead datetime and timedelta objects
            if issue_dt:
                parsed_arg_parts[self.ISSUE] = issue_dt
            if valid_dt:
                parsed_arg_parts[self.VALID] = valid_dt
            if issue_dt and valid_dt:
                parsed_arg_parts[self.LEAD] = TimeDelta(valid_dt - issue_dt)
            if leaf_dir := self._get_leafdir_from_arg_parts(parsed_arg_parts):
                parsed_arg_parts[self.LEAFDIR] = leaf_dir

            # cache this path and the parsed_arg_parts for repeat requests
            self._last_parsed_path = path
            self._parsed_args = parsed_arg_parts

    def _get_parsed_arg_parts(self, path: str, fmt_str: str) -> dict:
        """Build a dictionary of knowable variable based on path and format string. This
           dictionary can be used to create complete issue/valid datetimes and/or contain
           extra variables.

        Args:
            path (str): The path string from which variables will be extracted
            fmt_str (str): The format string used to identify where variables can be found

        Raises:
            ValueError: If the path string does not conform to the format string (not expected len)

        Returns:
            dict: Dictionary of variables
        """
        # Split path and format strings into lists of parts, either dir and/or filenames
        fmt_parts = os.path.normpath(fmt_str).split(os.sep)
        path_parts = os.path.normpath(path).split(os.sep)

        parsed_arg_parts = {}
        for path_part, fmt_part in zip(path_parts, fmt_parts):
            expected_len, lookup_info = self._lookup_dict[fmt_part]
            if (part_len := len(path_part)) != expected_len:
                raise ValueError(
                    "Path is not expected length. Passed path part "
                    f"'{path_part}' doesn't match format '{fmt_part}'"
                )
            for lookup in lookup_info:
                if not (0 <= lookup.start <= part_len and 0 <= lookup.end <= part_len):
                    raise ValueError("Parse indices are out of range for path")
                try:
                    match lookup.type:
                        case self.INT:
                            parsed_arg_parts[lookup.key] = int(
                                path_part[lookup.start : lookup.end]
                            )
                        case self.FLOAT:
                            parsed_arg_parts[lookup.key] = float(
                                path_part[lookup.start : lookup.end]
                            )
                        case self.STR:
                            parsed_arg_parts[lookup.key] = path_part[lookup.start : lookup.end]
                except ValueError as exc:
                    raise ValueError("Unable to apply formatting") from exc
        return parsed_arg_parts

    def _apply_format(self, fmt_str: str, **kwargs) -> str:
        """Use the format string and any variables in the kwargs to build a path.

        Args:
            fmt_str (str): A format string, for part or a whole path

        Raises:
            ValueError: If the generated path part does not match expected length

        Returns:
            str: A string representation of a system path, combined with os specific separators
        """
        path_parts = []
        # we split the format string without normalizing to maintain user specified path
        # struct such as a double separator (sometime this can be needed)
        for fmt_part in fmt_str.split(os.sep):
            path_part = fmt_part.format_map(kwargs)
            if len(path_part) == self._lookup_dict[fmt_part].exp_len:
                path_parts.append(path_part)
            else:
                raise ValueError(
                    "Arguments generate a path that violate "
                    f"at least part of the format, part '{fmt_part}'"
                )
        return os.path.sep.join(path_parts)

    @staticmethod
    def _get_issue_from_arg_parts(
        parsed_args: dict, valid: datetime | None = None, lead: timedelta | None = None
    ) -> datetime:
        """Static method for creating an issue date/time from parsed arguments and optional inputs

        Args:
            parsed_args (dict): A dictionary of issue, valid and/or lead info resulting
                                from parsing a path, dir, or filename
            valid (datetime | None, optional): Depending on info found during parsing,
                                        valid date/time can be useful. Defaults to None.
            lead (timedelta | None, optional): Depending on info found during parsing, lead time
                                        can be useful. Defaults to None.

        Returns:
            datetime: Issue date/time
        """
        if "issue.year" in parsed_args:
            return datetime(
                parsed_args.get("issue.year"),
                parsed_args.get("issue.month"),
                parsed_args.get("issue.day"),
                parsed_args.get("issue.hour", 0),
                parsed_args.get("issue.minute", 0),
                parsed_args.get("issue.second", 0),
                parsed_args.get("issue.microsecond", 0),
                tzinfo=UTC,
            )
        if lead is None and "lead.hour" in parsed_args:
            lead = PathBuilder._get_lead_from_time_args(parsed_args)
        if valid is None and "valid.year" in parsed_args:
            valid = PathBuilder._get_valid_from_arg_parts(parsed_args)
        if valid and lead:
            return valid - lead
        return None

    @staticmethod
    def _get_valid_from_arg_parts(
        parsed_args: dict, issue: datetime | None = None, lead: timedelta | None = None
    ) -> datetime:
        """Static method for creating a valid date/time from parsed arguments and optional inputs

        Args:
            parsed_args (dict): A dictionary of issue, valid and/or lead info resulting
                                from parsing a path, dir, or filename
            issue (datetime | None, optional): Depending on info found during parsing,
                                        issue date/time can be useful. Defaults to None.
            lead (timedelta | None, optional): Depending on info found during parsing, lead time
                                        can be useful. Defaults to None.

        Returns:
            datetime: Valid date/time
        """
        if "valid.year" in parsed_args:
            return datetime(
                parsed_args.get("valid.year"),
                parsed_args.get("valid.month"),
                parsed_args.get("valid.day"),
                parsed_args.get("valid.hour", 0),
                parsed_args.get("valid.minute", 0),
                parsed_args.get("valid.second", 0),
                parsed_args.get("valid.microsecond", 0),
                tzinfo=UTC,
            )
        if lead is None and "lead.hour" in parsed_args:
            lead = PathBuilder._get_lead_from_time_args(parsed_args)
        if issue is None and "issue.year" in parsed_args:
            issue = PathBuilder._get_issue_from_arg_parts(parsed_args)
        if issue and lead:
            return issue + lead
        return None

    @staticmethod
    def _get_lead_from_time_args(time_args: dict) -> timedelta | None:
        """Static method for creating a lead time from parsed arguments and optional inputs

        Args:
            time_args (dict): A dictionary of issue, valid and/or lead info resulting from parsing
                                a path, dir, or filename. Depending on info found during parsing,
                                issue or valid date/time.
        Returns:
            timedelta | None: Lead time, or None if lead.hour not in PathBuilder's format string
        """
        if "lead.hour" in time_args.keys():
            return timedelta(hours=time_args["lead.hour"])
        return None

    @staticmethod
    def _ensure_lead(
        issue: datetime | None, valid: datetime | None, lead: timedelta | TimeDelta | None
    ) -> TimeDelta:
        """Make every attempt to ensure lead is known, by calculating or converting if needed.

        Args:
            issue (datetime | None): An issue datetime if known, else None
            valid (datetime | None): A valid datetime if known, else None
            lead (timedelta | TimeDelta | None): A lead if known, else None

        Returns:
            TimeDelta: _description_
        """
        if lead:
            if isinstance(lead, timedelta):
                return TimeDelta(lead)
            return lead
        if issue and valid:
            return TimeDelta(valid - issue)
        return None

    @staticmethod
    def _get_leafdir_from_arg_parts(parsed_args: dict) -> str | None:
        """Static method to get optional `leafdir` from parsed format string arguments.
        Returns the leafdir argument (str) or None if it does not exist.
        """
        return parsed_args.get("leafdir")


# Private utility classes
class _LookupInfo(NamedTuple):
    """Data class used to hold lookup info"""

    key: str
    start: int
    end: int
    type: str  # should be one of 'd', 'f', 's'


class _FormatLookup(NamedTuple):
    """Data class used to hold format and lookup info"""

    exp_len: int
    lookups: list[_LookupInfo]

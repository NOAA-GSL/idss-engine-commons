"""A collection of useful classes and utility functions"""
# -------------------------------------------------------------------------------
# Created on Wed Feb 15 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# -------------------------------------------------------------------------------

import copy
import logging
from datetime import datetime, timedelta, timezone
from subprocess import Popen, PIPE, TimeoutExpired
from typing import Sequence

logger = logging.getLogger(__name__)


class TimeDelta():
    """Wrapper class for datetime.timedelta to add helpful properties"""
    def __init__(self, time_delta: timedelta) -> None:
        self._td = time_delta

    @property
    def minute(self):
        """Property to get the number of minutes this instance represents"""
        return int(self._td / timedelta(minutes=1))

    @property
    def hour(self):
        """Property to get the number of hours this instance represents"""
        return int(self._td / timedelta(hours=1))

    @property
    def day(self):
        """Property to get the number of days this instance represents"""
        return self._td.days


class Map(dict):
    """Wrapper class for python dictionary with dot access"""
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


def exec_cmd(commands: Sequence[str], timeout: int = None) -> Sequence[str]:
    """Execute the passed commands via a Popen call

    Args:
        commands (Sequence[str]): The commands to be executed

    Raises:
        RuntimeError: When execution results in an error code

    Returns:
        Sequence[str]: Result of executing the commands
    """
    logger.debug('Making system call %s', commands)
    # with Popen(commands, stdout=PIPE, stderr=PIPE) as proc:
    #     out = proc.readlines()
    process = Popen(commands, stdout=PIPE, stderr=PIPE)
    try:
        outs, errs = process.communicate(timeout=timeout)
    except TimeoutExpired:
        process.kill()
        outs, errs = process.communicate()
    if process.returncode != 0:
        # the process was not successful
        raise OSError(process.returncode, errs.decode())
    try:
        ans = outs.decode().splitlines()
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise RuntimeError(e) from e
    return ans


def to_iso(date_time: datetime) -> str:
    """Format a datetime instance to an ISO string"""
    logger.debug('Datetime (%s) to iso', datetime)
    return (f'{date_time.strftime("%Y-%m-%dT%H:%M")}:'
            f'{(date_time.second + date_time.microsecond / 1e6):06.3f}'
            f'{"Z" if date_time.tzinfo in [None, timezone.utc] else date_time.strftime("%Z")[3:]}')


def to_compact(date_time: datetime) -> str:
    """Format a datetime instance to an compact string"""
    logger.debug('Datetime (%s) to compact -- %s', datetime, __name__)
    return date_time.strftime('%Y%m%d%H%M%S')


def hash_code(string: str) -> int:
    """Creates a hash code from provided string

    Args:
        string (str): String to be hashed

    Returns:
        int: hash code
    """
    hash_ = 0
    for char in string:
        hash_ = int((((31 * hash_ + ord(char)) ^ 0x80000000) & 0xFFFFFFFF) - 0x80000000)
    return hash_


def dict_copy_with(old_dict: dict, **kwargs) -> dict:
    """Perform a deep copy a dictionary and adds additional key word arguments

    Args:
        old_dict (dict): The old dictionary to be copied

    Returns:
        dict: New dictionary
    """
    new_dict = copy.deepcopy(old_dict)
    for key, value in kwargs.items():
        new_dict[key] = value
    return new_dict


def datetime_gen(dt_: datetime,
                 time_delta: timedelta,
                 end_dt: datetime = None,
                 max_num: int = 100) -> datetime:
    """Create a date/time sequence generator, given a starting date/time and a time stride

    Args:
        dt_ (datetime): Starting date/time, will be the first date/time made available
        time_delta (timedelta): Time delta, can be either positive or negative
        end_dt (datetime, optional): Ending date/time, will be the last. Defaults to None.
        max_num (int, optional): Max number of date/times that generator will return.
                                 Defaults to 100.

    Yields:
        datetime: Next date/time in sequence
    """
    if end_dt:
        dt_cnt = int((end_dt-dt_)/time_delta)+1
        max_num = min(max_num, dt_cnt) if max_num else dt_cnt

    for i in range(0, max_num):
        logger.debug('dt generator %d/%d', i, max_num)
        yield dt_ + time_delta * i

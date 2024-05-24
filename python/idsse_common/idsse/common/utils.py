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
import math
from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from enum import Enum
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any, Generator
from uuid import UUID

logger = logging.getLogger(__name__)


class RoundingMethod(Enum):
    """Transformations indicators to be applied to numbers when rounding to ints"""
    ROUND = 'ROUND'
    FLOOR = 'FLOOR'


RoundingParam = str | RoundingMethod


class TimeDelta:
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
        super().__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value

        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]


def exec_cmd(commands: Sequence[str], timeout: int | None = None) -> Sequence[str]:
    """Execute the passed commands via a Popen call

    Args:
        commands (Sequence[str]): The commands to be executed
        timeout :
    Raises:
        RuntimeError: When execution results in an error code

    Returns:
        Sequence[str]: Result of executing the commands
    """
    logger.debug('Making system call %s', commands)
    with Popen(commands, stdout=PIPE, stderr=PIPE) as process:
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
    except Exception as exc:  # pylint: disable=broad-exception-caught
        raise RuntimeError(exc) from exc
    return ans


def to_iso(date_time: datetime) -> str:
    """Format a datetime instance to an ISO string"""
    logger.debug('Datetime (%s) to iso', datetime)
    return (f'{date_time.strftime("%Y-%m-%dT%H:%M")}:'
            f'{(date_time.second + date_time.microsecond / 1e6):06.3f}'
            'Z' if date_time.tzname() in [None, str(timezone.utc)]
            else date_time.strftime("%Z")[3:])


def to_compact(date_time: datetime) -> str:
    """Format a datetime instance to a compact string"""
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


def datetime_gen(dt_start: datetime,
                 time_delta: timedelta,
                 dt_end: datetime | None = None,
                 max_num: int = 100) -> Generator[datetime, Any, None]:
    """Create a date/time sequence generator, given a starting date/time and a time stride

    Args:
        dt_start (datetime): Starting date/time, will be the first date/time made available
        time_delta (timedelta): Time delta, can be either positive or negative. The sign of this
                                will be switch based on the order of start_dt and end_dt.
        dt_end (datetime | None, optional): Ending date/time, will be the last, unless generation is
                                     halted by max_num. Defaults to None.
        max_num (int, optional): Max number of date/times that generator will return.
                                 Defaults to 100.

    Yields:
        datetime: Next date/time in sequence
    """
    if dt_end:
        time_delta_pos = time_delta > timedelta(seconds=0)

        if (dt_start > dt_end and time_delta_pos) or \
                (dt_start < dt_end and not time_delta_pos):
            time_delta = timedelta(seconds=-1.0 * time_delta.total_seconds())

        dt_cnt = int((dt_end - dt_start) / time_delta) + 1
        max_num = min(max_num, dt_cnt) if max_num else dt_cnt

    for i in range(0, max_num):
        logger.debug('dt generator %d/%d', i, max_num)
        yield dt_start + time_delta * i


def _round_away_from_zero(number: float) -> int:
    func = math.floor if number < 0 else math.ceil
    return func(number)


def _round_toward_zero(number: float) -> int:
    func = math.ceil if number < 0 else math.floor
    return func(number)

def round_half_away(number: int | float, precision: int = 0) -> int | float:
    """
    *Deprecated: avoid using this function directly, instead use idsse.commons.round_()*

    Round a float to a set number of decimal places, using "ties away from zero" method,
    in contrast with Python 3's built-in round() or numpy.round() functions, both which
    use "ties to even" method.

    | Input | round() | round_half_away() |
    | ----- | ------- | ----------------- |
    |   2.5 |       2 |                 3 |
    | -14.5 |     -14 |               -15 |

    Args:
        number (int | float | numpy.int | numpy.float_): a scalar value from a Python/numpy array
        precision (int): number of decimal places to preserve.

    Returns:
        (int | float): rounded number as int if precision is 0, otherwise as float
    """
    factor = 10 ** precision
    factored_number = number * factor
    is_less_than_half = abs(factored_number - math.trunc(factored_number)) < 0.5

    rounded_number = (
        _round_toward_zero(factored_number) if is_less_than_half
        else _round_away_from_zero(factored_number)
    ) / factor
    return int(rounded_number) if precision == 0 else float(rounded_number)


def round_(
    number: int | float,
    precision: int = 0,
    rounding: RoundingParam = RoundingMethod.ROUND
) -> int | float:
    """
    Round a float to a set number of decimal places, using "ties away from zero" method if rounding
    is RoundingMethod.ROUND or math.floor() if RoundingMethod.FLOOR.

    This behavior contrasts with Python 3's built-in round() or numpy.round() functions,
    which use "ties to even" method.

    | Input | round() | round_half_away() |
    | ----- | ------- | ----------------- |
    |   2.5 |       2 |                 3 |
    | -14.5 |     -14 |               -15 |

    Args:
        number (int | float | numpy.int | numpy.float_): a number, often from a Python/numpy array
        precision (int): number of decimal places to preserve. Defaults to 0.
        rounding (RoundingMethod | str, optional): how number should be rounded. Either "nearest
            integer, ties away from zero", or math.floor(). Defaults to RoundingMethod.ROUND.

    Raises:
        ValueError: if rounding argument is invalid.

    Returns:
        (int | float): rounded number as int if precision is 0, otherwise as float
    """
    if isinstance(rounding, str):  # cast str to RoundingMethod enum
        try:
            rounding = RoundingMethod[rounding.upper()]
        except KeyError as exc:
            raise ValueError(f'Unsupported rounding method {rounding}') from exc

    if rounding is RoundingMethod.ROUND:
        return round_half_away(number, precision)
    if rounding is RoundingMethod.FLOOR:
        return math.floor(number)
    raise ValueError('rounding method cannot be None')


def round_values(
    *args: int | float,
    rounding: RoundingParam | None,
    precision: int = 0,
) -> list[int | float]:
    """Round a list/tuple of floats to a given number of decimal places, default 0.

    Args:
        *args: all scalar values to be rounded
        rounding (RoundingParam | None): one of None, 'round', 'floor'. Default is None.
        precision (int): Number of decimal places to preserve. Default is 0.
    """
    if rounding is None:
        return [int(v) for v in args]
    return [round_(v, precision=precision, rounding=rounding) for v in args]


def is_valid_uuid(uuid: str, version=4) -> bool:
    """Checks for a valid UUID

    Args:
        uuid (str): String to be checked
        version (int) : Expect UUID version

    Returns:
        bool: result of check
    """
    try:
        UUID(uuid, version=version)
    except ValueError:
        return False
    return True

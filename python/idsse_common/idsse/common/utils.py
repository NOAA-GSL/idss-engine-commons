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
import os
from collections.abc import Sequence
from datetime import datetime, timedelta, UTC
from enum import Enum
from subprocess import PIPE, Popen, TimeoutExpired
from time import sleep
from typing import Any, Generator
from uuid import UUID

logger = logging.getLogger(__name__)


class RoundingMethod(Enum):
    """Transformations indicators to be applied to numbers when rounding to ints"""
    ROUND = 'ROUND'
    FLOOR = 'FLOOR'


RoundingParam = str | RoundingMethod


class TimeDelta(timedelta):
    """Extend class for datetime.timedelta to add helpful properties."""
    def __new__(cls, *args, **kwargs):
        if isinstance(args[0], timedelta):
            return super().__new__(cls, seconds=args[0].total_seconds())
        return super().__new__(cls, *args, **kwargs)

    @property
    def minute(self):
        """Property to get the number of minutes this instance represents"""
        return int(self / timedelta(minutes=1))

    @property
    def minutes(self):
        """Property to get the number of minutes this instance represents"""
        return self.minute

    @property
    def hour(self):
        """Property to get the number of hours this instance represents"""
        return int(self / timedelta(hours=1))

    @property
    def hours(self):
        """Property to get the number of hours this instance represents"""
        return self.hour

    @property
    def day(self):
        """Property to get the number of days this instance represents"""
        return self.days


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


class FileBasedLock():
    """
    Ensure atomic read/write of a given file using only the filesystem; behavior is the same
    whether workers accessing the file are distributed across Python threads, subprocesses,
    Docker containers, VMs, etc.

    Note: this thread must have permissions to WRITE as well as read on the filesystem where
    this file is stored.

    Example usage:
    ```
    file_of_interest = './foo.txt'
    with FileBasedLock(file_of_interest):
        # now guaranteed that no other process on any machine is accessing this file
        with open(file_of_interest, 'a') as f:
            f.write('hello world')
    # lock is now released for other threads/processes
    ```
    """
    def __init__(self, filepath: str, max_age: float):
        """
        Args:
            filepath (str): The file on which the caller wants to do atomic I/O (read/write)
            max_age (float): The maximum time (seconds) after which a `.lock` file will be treated
                as `expired` or "orphaned" by a process/thread that was unexpectedly exited.
                FileBasedLocks are auto-released after this duration and the original locker
                loses all guarantees of atomicity. Recommended to keep this short (10 minutes?),
                based on how long a single thread could reasonably being expected to read/write
                for this file type and usage.
        """
        self.filepath = os.path.abspath(filepath)
        self._lock_path = f'{self.filepath}.lock'
        self._max_age = max_age

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    @property
    def locked(self) -> bool:
        """True if some thread has already locked this file resource"""
        return os.path.exists(self._lock_path)

    @property
    def expired(self) -> bool:
        """True if lock is older than `_max_age` seconds and should be considered orphaned"""
        if not self.locked:
            return False  # lock cannot be expired if it isn't locked

        try:
            creation_time = os.stat(self._lock_path).st_birthtime
        except AttributeError:
            # Linux (and maybe Windows) don't support birthtime
            creation_time = os.stat(self._lock_path).st_ctime
        except FileNotFoundError:
            # lock file disappeared since start of function call?? *shrug* treat it as unexpired
            creation_time = datetime.now(UTC).timestamp()
        return (datetime.now(UTC).timestamp() - creation_time) >= self._max_age

    def acquire(self, timeout=300.0) -> bool:
        """Block until the desired file (declared in FileLock __init__) is free to read/write.
        Does this by creating a `.lock` file that communicates to other `FileBasedLock` instances
        that this file is in use.

        If `_max_age` has passed, lock will be forcefully released before acquiring for this caller.

        Args:
            timeout (float, optional): Number of seconds until TimeoutError will be raised.
                Defaults to 300.

        Raises:
            TimeoutError: if timeout was exceeded waiting for lock to be released
        """

        wait_ms = 0
        while self.locked and not self.expired and wait_ms / 1000 < timeout:
            sleep(0.01)
            wait_ms += 10

        if wait_ms / 1000 >= timeout:
            raise TimeoutError

        if self.expired:
            self.release()  # _max_age has passed, consider this lock abandoned and delete it

        self._create_lockfile()  # this actually acquires the lock
        return True

    def release(self) -> bool:
        """Release the lock so other processes/threads can do I/O"""
        if not self.locked:
            return False
        os.remove(self._lock_path)
        return True

    def _create_lockfile(self):
        """The actual functionality triggered by `acquire()` (after lock is confirmed free)"""
        os.makedirs(os.path.dirname(self._lock_path), exist_ok=True)
        with open(self._lock_path, 'w', encoding='utf-8') as file:
            file.write('')


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
    return (f'{date_time.strftime("%Y-%m-%dT%H:%M")}:'
            f'{(date_time.second + date_time.microsecond / 1e6):06.3f}'
            'Z' if date_time.tzname() in [None, str(UTC)]
            else date_time.strftime("%Z")[3:])


def to_compact(date_time: datetime) -> str:
    """Format a datetime instance to a compact string"""
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

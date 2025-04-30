"""Test suite for utils.py"""
# --------------------------------------------------------------------------------
# Created on Mon Mar 20 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# --------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,invalid-name,redefined-outer-name

import os
from copy import deepcopy
from datetime import datetime, timedelta
from math import pi
from os import path
from time import sleep
from uuid import uuid4

import pytest

from idsse.common.utils import TimeDelta, Map, FileBasedLock
from idsse.common.utils import (
    datetime_gen,
    dict_copy_with,
    exec_cmd,
    is_valid_uuid,
    hash_code,
    round_,
    round_half_away,
    to_compact,
    to_iso
)


def test_timedelta_minute():
    td = TimeDelta(timedelta(minutes=13))
    assert td.minute == 13


def test_timedelta_hour():
    td = TimeDelta(timedelta(hours=14))
    assert td.hour == 14


def test_timedelta_day():
    td = TimeDelta(timedelta(days=15))
    assert td.day == 15


def test_map_dict_init_with_args():
    example_dict = {'value': 123, 'metadata': { 'other_data': [100, 200]}}
    example_map = Map(example_dict)

    # pylint: disable=no-member
    assert example_map.value == 123
    assert example_map.metadata == {'other_data': [100, 200]}


def test_map_dict_init_with_kwargs():
    example_map = Map(value=123, metadata={'other_data': [100, 200]})

    # pylint: disable=no-member
    assert example_map.value == 123
    assert example_map.metadata == {'other_data': [100, 200]}


def test_map_dict_set_value():
    example_map = Map(value=123, metadata={'other_data': [100, 200]})
    example_map.value = 321  # change value
    # pylint: disable=no-member
    assert example_map.value == 321


def test_exec_cmd():
    current_dir = path.dirname(__file__)
    result = exec_cmd(['ls', current_dir])

    # verify that at least __init__ and this file were found
    assert '__init__.py' in result
    assert __file__.split(path.sep, maxsplit=-1)[-1] in result


def test_to_iso():
    dt = datetime(2013, 12, 11, 10, 9, 8)
    assert to_iso(dt) == '2013-12-11T10:09:08.000Z'


def test_to_compact():
    dt = datetime(2013, 12, 11, 10, 9, 8)
    assert to_compact(dt) == '20131211100908'


@pytest.mark.parametrize('string, hash_code_', [('Everyone is equal', 1346529203),
                                                ('You are awesome', -1357061130)])
def test_hash_code(string, hash_code_):
    assert hash_code(string) == hash_code_


def test_dict_copy_with():
    starting_dict = { 'value': 123, 'units': 'mph'}
    copied_dict = deepcopy(starting_dict)

    # run copy
    result = dict_copy_with(
        copied_dict, source='speedometer', metadata={'some': ('other', 'data')}
    )

    # original dict should be unchanged
    assert copied_dict == starting_dict
    assert 'source' not in copied_dict

    # starting values should exist in result
    assert result['value'] == starting_dict['value']
    assert result['units'] == starting_dict['units']

    # new values should also have been added to result
    assert result['source'] == 'speedometer'
    assert result['metadata'] == {'some': ('other', 'data')}


def test_datetime_gen_forward():
    dt_start = datetime(2021, 1, 2, 3)
    time_delta = timedelta(hours=1)
    max_num = 5

    dts_found = list(datetime_gen(dt_start, time_delta, max_num=max_num))
    assert dts_found == [datetime(2021, 1, 2, 3, 0),
                         datetime(2021, 1, 2, 4, 0),
                         datetime(2021, 1, 2, 5, 0),
                         datetime(2021, 1, 2, 6, 0),
                         datetime(2021, 1, 2, 7, 0)]


def test_datetime_gen_backwards():
    dt_start = datetime(2021, 1, 2, 3)
    time_delta = timedelta(days=-1)
    max_num = 4

    dts_found = list(datetime_gen(dt_start, time_delta, max_num=max_num))
    assert dts_found == [datetime(2021, 1, 2, 3, 0),
                         datetime(2021, 1, 1, 3, 0),
                         datetime(2020, 12, 31, 3, 0),
                         datetime(2020, 12, 30, 3, 0)]


def test_datetime_gen_bound():
    dt_start = datetime(2021, 1, 2, 3)
    time_delta = timedelta(weeks=2)
    dt_end = datetime(2021, 1, 30, 3)

    dts_found = list(datetime_gen(dt_start, time_delta, dt_end))
    assert dts_found == [datetime(2021, 1, 2, 3, 0),
                         datetime(2021, 1, 16, 3, 0),
                         datetime(2021, 1, 30, 3, 0)]


def test_datetime_gen_switch_time_delta_sign():
    dt_start = datetime(2021, 1, 2, 3)
    time_delta = timedelta(weeks=-2)
    dt_end = datetime(2021, 1, 30, 3)

    dts_found = list(dt_ for dt_ in datetime_gen(dt_start, time_delta, dt_end))
    assert dts_found == [datetime(2021, 1, 2, 3, 0),
                         datetime(2021, 1, 16, 3, 0),
                         datetime(2021, 1, 30, 3, 0)]


@pytest.mark.parametrize('number, expected', [(2.50000, 3), (-14.5000, -15), (3.49999, 3)])
def test_round_half_away_int(number: float, expected: int):
    result = round_half_away(number)
    assert isinstance(result, int)
    assert result == expected


@pytest.mark.parametrize('number, expected', [(9.5432, 9.5), (-0.8765, -0.9)])
def test_round_half_away_float(number: float, expected: float):
    result = round_half_away(number, precision=1)
    assert isinstance(result, float)
    assert result == expected


@pytest.mark.parametrize('number, expected',
                  [(100.987654321, 100.988), (-43.21098, -43.211), (pi, 3.142)])
def test_round_half_away_with_precision(number: float, expected: float):
    result = round_half_away(number, precision=3)
    assert isinstance(result, float)
    assert result == expected


def test_invalid_rounding_method_raises_error():
    with pytest.raises(ValueError) as exc:
        round_(123.456, rounding='MAGIC')
    assert 'MAGIC' in exc.value.args[0]

    with pytest.raises(ValueError) as exc:
        round_(123.456, rounding=None)
    assert 'None' in exc.value.args[0]


def test_is_valid_uuid_success():
    assert is_valid_uuid('f848406c-44eb-491f-99df-d0461090425c')
    assert is_valid_uuid('f848406c-44eb-491f-99df-d0461090425c', version=4)
    assert is_valid_uuid('1d10609e-ba56-11ee-af51-fa605d1346b6', version=1)


def test_is_valid_uuid_failure():
    assert not is_valid_uuid('abc-def-ghi-jlk')  # badly-formed UUID
    assert not is_valid_uuid('1d10609e-ba56-11ee-af51-fa605d1346b6', version=7)  # invalid version


@pytest.fixture
def example_file():
    return f'./tmp/{uuid4()}'


@pytest.fixture(autouse=True)
def auto_cleanup(example_file: str):
    # ensure any previous test .lock files are cleaned up
    if os.path.exists(example_file):
        os.remove(example_file)

    yield

    if os.path.exists(example_file):
        os.remove(example_file)
    if os.path.exists(os.path.dirname(example_file)):
        os.rmdir(os.path.dirname(example_file))


def test_lock_acquire(example_file):
    lock = FileBasedLock(example_file, max_age=600)
    assert not lock.locked

    lock.acquire()
    assert lock.locked

    lock.release()
    assert not lock.locked


def test_lock_expired(example_file):
    lock = FileBasedLock(example_file, max_age=0.001)
    lock.acquire()
    sleep(0.002)

    assert lock.expired
    lock.release()


def test_lock_timeout(example_file):
    lock = FileBasedLock(example_file, max_age=60)
    lock.acquire()

    with pytest.raises(TimeoutError) as exc:
        lock.acquire(0.1)
    assert exc is not None
    lock.release()  # cleanup lock


def test_lock_creates_parent_dir():
    parent_dir_a = './foo'
    parent_dir_b = 'bar'
    file_to_download = f'{parent_dir_a}/{parent_dir_b}/baz.txt'
    assert not os.path.exists(parent_dir_a)
    lock = FileBasedLock(file_to_download, max_age=60)

    lock.acquire()  # acquire() will magically create all nested parent dirs for .lock
    assert lock.locked
    assert os.path.exists(f'{parent_dir_a}/{parent_dir_b}')

    # clean up lock and temporary parent dirs created for the lock
    lock.release()
    os.rmdir(f'{parent_dir_a}/{parent_dir_b}')
    os.rmdir(parent_dir_a)
    assert not os.path.exists(parent_dir_a)

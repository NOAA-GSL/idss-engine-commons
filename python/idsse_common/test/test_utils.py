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

from copy import deepcopy
from datetime import datetime, timedelta
from os import path
from math import pi
import pytest


from idsse.common.utils import TimeDelta, Map
from idsse.common.utils import datetime_gen, hash_code, exec_cmd, to_compact, to_iso, dict_copy_with, round_half_away


# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

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
    assert to_iso(dt) == '2013-12-11T10:09:08Z'


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
    result = dict_copy_with(copied_dict, source='speedometer', metadata={'some': ('other', 'data')})

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
    dt_ = datetime(2021, 1, 2, 3)
    time_delta = timedelta(hours=1)
    max_num = 5

    dts_found = [dt_ for dt_ in datetime_gen(dt_, time_delta, max_num=max_num)]
    assert dts_found == [datetime(2021, 1, 2, 3, 0),
                         datetime(2021, 1, 2, 4, 0),
                         datetime(2021, 1, 2, 5, 0),
                         datetime(2021, 1, 2, 6, 0),
                         datetime(2021, 1, 2, 7, 0)]


def test_datetime_gen_backwards():
    dt_ = datetime(2021, 1, 2, 3)
    time_delta = timedelta(days=-1)
    max_num = 4

    dts_found = [dt_ for dt_ in datetime_gen(dt_, time_delta, max_num=max_num)]
    assert dts_found == [datetime(2021, 1, 2, 3, 0),
                         datetime(2021, 1, 1, 3, 0),
                         datetime(2020, 12, 31, 3, 0),
                         datetime(2020, 12, 30, 3, 0)]


def test_datetime_gen_bound():
    dt_ = datetime(2021, 1, 2, 3)
    time_delta = timedelta(weeks=2)
    end_dt = datetime(2021, 1, 30, 3)

    dts_found = [dt_ for dt_ in datetime_gen(dt_, time_delta, end_dt)]
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


@pytest.mark.parametrize('number, expected', [(100.987654321, 100.988), (-43.21098, -43.211), (pi, 3.142)])
def test_round_half_away_with_precision(number: float, expected: float):
    result = round_half_away(number, precision=3)
    assert isinstance(result, float)
    assert result == expected

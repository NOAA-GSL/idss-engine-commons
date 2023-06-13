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

import pytest  # pylint: disable=import-error
from datetime import datetime, timedelta


from idsse.common.utils import TimeDelta
from idsse.common.utils import datetime_gen, hash_code, to_compact, to_iso


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

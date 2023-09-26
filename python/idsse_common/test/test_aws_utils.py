"""Test suite for aws_utils.py"""
# --------------------------------------------------------------------------------
# Created on Wed Jun 21 2023
#
# Copyright (c) 2023 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# --------------------------------------------------------------------------------

from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock

from pytest import fixture, MonkeyPatch

from idsse.common.aws_utils import AwsUtils

# pylint: disable=missing-function-docstring,redefined-outer-name,pointless-statement
# pylint: disable=invalid-name,unused-argument

EXAMPLE_ISSUE = datetime(1970, 10, 3, 12)
EXAMPLE_VALID = datetime(1970, 10, 3, 14)

EXAMPLE_DIR = 's3://noaa-nbm-grib2-pds/blend.19701003/12/core/'
EXAMPLE_FILES = ['blend.t12z.core.f002.co.grib2',
                 'blend.t12z.core.f003.co.grib2',
                 'blend.t12z.core.f004.co.grib2']


# fixtures
@fixture
def aws_utils() -> AwsUtils:
    EXAMPLE_BASE_DIR = 's3://noaa-nbm-grib2-pds/'
    EXAMPLE_SUB_DIR = ('blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/'
                       '{issue.hour:02d}/core/')
    EXAMPLE_FILE_BASE = 'blend.t{issue.hour:02d}z.core.f{lead.hour:03d}'
    EXAMPLE_FILE_EXT = '.co.grib2'

    return AwsUtils(EXAMPLE_BASE_DIR, EXAMPLE_SUB_DIR, EXAMPLE_FILE_BASE, EXAMPLE_FILE_EXT)


@fixture
def aws_utils_with_wild() -> AwsUtils:
    EXAMPLE_BASE_DIR = 's3://noaa-nbm-grib2-pds/'
    EXAMPLE_SUB_DIR = ('blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/'
                       '{issue.hour:02d}/core/')
    EXAMPLE_FILE_BASE = 'blend.t{issue.hour:02d}z.core.f?{lead.hour:02d}'
    EXAMPLE_FILE_EXT = '.co.grib2'

    return AwsUtils(EXAMPLE_BASE_DIR, EXAMPLE_SUB_DIR, EXAMPLE_FILE_BASE, EXAMPLE_FILE_EXT)


@fixture
def mock_exec_cmd(monkeypatch: MonkeyPatch) -> Mock:
    def get_files_for_dir(args: List[str]) -> List[str]:
        hour = args[-1].split('/')[-3]
        return [f'blend.t{hour}z.core.f002.co.grib2',
                f'blend.t{hour}z.core.f003.co.grib2',
                f'blend.t{hour}z.core.f004.co.grib2']
    mock_function = Mock(side_effect=get_files_for_dir)
    monkeypatch.setattr('idsse.common.aws_utils.exec_cmd', mock_function)
    return mock_function


# test class methods
def test_get_path(aws_utils: AwsUtils):
    result_path = aws_utils.get_path(EXAMPLE_ISSUE, EXAMPLE_VALID)
    assert result_path == f'{EXAMPLE_DIR}blend.t12z.core.f002.co.grib2'


def test_aws_ls(aws_utils: AwsUtils, mock_exec_cmd):
    result = aws_utils.aws_ls(EXAMPLE_DIR)

    assert len(result) == len(EXAMPLE_FILES)
    assert result[0] == f'{EXAMPLE_DIR}{EXAMPLE_FILES[0]}'
    mock_exec_cmd.assert_called_once()


def test_aws_ls_without_prepend_path(aws_utils: AwsUtils, mock_exec_cmd):
    result = aws_utils.aws_ls(EXAMPLE_DIR, prepend_path=False)

    assert len(result) == len(EXAMPLE_FILES)
    assert result[0] == EXAMPLE_FILES[0]
    mock_exec_cmd.assert_called_once()


def test_aws_ls_retries_with_s3_command_line(aws_utils: AwsUtils, monkeypatch: MonkeyPatch):
    # fails first call, succeeds second call
    mock_exec_cmd_failure = Mock(
        side_effect=[FileNotFoundError, EXAMPLE_FILES])
    monkeypatch.setattr('idsse.common.aws_utils.exec_cmd',
                        mock_exec_cmd_failure)

    result = aws_utils.aws_ls(EXAMPLE_DIR)
    assert len(result) == 3  # ls should have eventually returned good data
    assert mock_exec_cmd_failure.call_count == 2


def test_aws_ls_returns_empty_array_on_error(aws_utils: AwsUtils, monkeypatch: MonkeyPatch):
    mock_exec_cmd_failure = Mock(side_effect=PermissionError('No permissions'))
    monkeypatch.setattr('idsse.common.aws_utils.exec_cmd',
                        mock_exec_cmd_failure)

    result = aws_utils.aws_ls(EXAMPLE_DIR)
    assert result == []
    mock_exec_cmd_failure.assert_called_once


def test_aws_cp_succeeds(aws_utils: AwsUtils, mock_exec_cmd):
    path = f'{EXAMPLE_DIR}file.grib2.idx'
    dest = f'{EXAMPLE_DIR}new_file.grib2.idx'

    copy_success = aws_utils.aws_cp(path, dest)
    assert copy_success


def test_aws_cp_retries_with_s3_command_line(aws_utils: AwsUtils, monkeypatch: MonkeyPatch):
    mock_exec_cmd_failure = Mock(
        side_effect=[FileNotFoundError, ['cp worked']])
    monkeypatch.setattr('idsse.common.aws_utils.exec_cmd',
                        mock_exec_cmd_failure)

    copy_success = aws_utils.aws_cp('s3:/some/path', 's3:/new/path')
    assert copy_success
    assert mock_exec_cmd_failure.call_count == 2


def test_aws_cp_fails(aws_utils: AwsUtils, monkeypatch: MonkeyPatch):
    mock_exec_cmd_failure = Mock(
        side_effect=[FileNotFoundError, Exception('unexpected bad thing happened')])
    monkeypatch.setattr('idsse.common.aws_utils.exec_cmd',
                        mock_exec_cmd_failure)

    copy_success = aws_utils.aws_cp('s3:/some/path', 's3:/new/path')
    assert not copy_success
    mock_exec_cmd_failure.call_count == 2


def test_check_for_succeeds(aws_utils: AwsUtils, mock_exec_cmd):
    result = aws_utils.check_for(EXAMPLE_ISSUE, EXAMPLE_VALID)
    assert result is not None
    assert result == (EXAMPLE_VALID, f'{EXAMPLE_DIR}{EXAMPLE_FILES[0]}')


def test_check_for_does_not_find_valid(aws_utils: AwsUtils, mock_exec_cmd):
    unexpected_valid = datetime(1970, 10, 3, 23)
    result = aws_utils.check_for(EXAMPLE_ISSUE, unexpected_valid)
    assert result is None


def test_get_issues(aws_utils: AwsUtils, mock_exec_cmd):
    result = aws_utils.get_issues(
        issue_start=EXAMPLE_ISSUE, issue_end=EXAMPLE_VALID, num_issues=2)
    assert len(result) == 2
    assert result[0] == EXAMPLE_VALID
    assert result[1] == EXAMPLE_VALID - timedelta(hours=1)


def test_get_issues_with_same_start_stop(aws_utils: AwsUtils, mock_exec_cmd):
    result = aws_utils.get_issues(issue_start=EXAMPLE_ISSUE, issue_end=EXAMPLE_ISSUE)
    assert len(result) == 1
    assert result[0] == EXAMPLE_ISSUE


def test_get_issues_latest_issue_from_today_if_no_args_passed(aws_utils: AwsUtils,
                                                              mock_exec_cmd):

    result = aws_utils.get_issues()
    # with current mocks returned issue (latest issue) will always be "now" with
    # truncated minute, second, and microsecond
    assert len(result) == 1
    assert result[0] == datetime.utcnow().replace(minute=0, second=0, microsecond=0)


def test_get_valids_all(aws_utils: AwsUtils, mock_exec_cmd):
    result = aws_utils.get_valids(EXAMPLE_ISSUE)
    assert len(result) == 3
    assert result[0] == (EXAMPLE_VALID, f'{EXAMPLE_DIR}{EXAMPLE_FILES[0]}')
    assert result[1] == (EXAMPLE_VALID + timedelta(hours=1), f'{EXAMPLE_DIR}{EXAMPLE_FILES[1]}')
    assert result[2] == (EXAMPLE_VALID + timedelta(hours=2), f'{EXAMPLE_DIR}{EXAMPLE_FILES[2]}')


def test_get_valids_with_start_filter(aws_utils: AwsUtils, mock_exec_cmd):
    valid_start = EXAMPLE_VALID + timedelta(hours=1)
    result = aws_utils.get_valids(EXAMPLE_ISSUE, valid_start=valid_start)
    assert len(result) == 2
    assert result[0] == (valid_start, f'{EXAMPLE_DIR}{EXAMPLE_FILES[1]}')
    assert result[1] == (valid_start + timedelta(hours=1), f'{EXAMPLE_DIR}{EXAMPLE_FILES[2]}')


def test_get_valids_with_start_and_end_filer(aws_utils: AwsUtils, mock_exec_cmd):
    valid_start = EXAMPLE_VALID
    valid_end = EXAMPLE_VALID + timedelta(hours=1)
    result = aws_utils.get_valids(EXAMPLE_ISSUE, valid_start=valid_start, valid_end=valid_end)
    assert len(result) == 2
    assert result[0] == (valid_start, f'{EXAMPLE_DIR}{EXAMPLE_FILES[0]}')
    assert result[1] == (valid_end, f'{EXAMPLE_DIR}{EXAMPLE_FILES[1]}')


def test_get_valids_with_same_start_end_filer(aws_utils: AwsUtils, mock_exec_cmd):
    valid_start = EXAMPLE_VALID
    valid_end = EXAMPLE_VALID + timedelta(hours=1)
    result_same = aws_utils.get_valids(EXAMPLE_ISSUE,
                                       valid_start=valid_start,
                                       valid_end=valid_start)
    result_diff = aws_utils.get_valids(EXAMPLE_ISSUE,
                                       valid_start=valid_start,
                                       valid_end=valid_end)
    assert len(result_same) == 1
    assert len(result_diff) == 2
    assert result_same[0] == result_diff[0]


def test_get_valids_with_wildcards(aws_utils_with_wild: AwsUtils, mock_exec_cmd):
    result = aws_utils_with_wild.get_valids(EXAMPLE_ISSUE)
    assert len(result) == 3
    assert result[0] == (EXAMPLE_VALID, f'{EXAMPLE_DIR}{EXAMPLE_FILES[0]}')
    assert result[1] == (EXAMPLE_VALID + timedelta(hours=1), f'{EXAMPLE_DIR}{EXAMPLE_FILES[1]}')
    assert result[2] == (EXAMPLE_VALID + timedelta(hours=2), f'{EXAMPLE_DIR}{EXAMPLE_FILES[2]}')

"""Test suite for path_builder.py"""
# --------------------------------------------------------------------------------
# Created on Thu Jun 15 2023
#
# Copyright (c) 2023 Colorado State University. All rights reserved.
#
# Contributors:
#     Mackenzie Grimes
#
# --------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,invalid-name,redefined-outer-name,protected-access
# cspell:words pathbuilder

from datetime import datetime, timedelta, UTC
from pytest import fixture, raises

from idsse.common.path_builder import TimeDelta, PathBuilder

# properties
EXAMPLE_BASE_DIR = './some/directory'
EXAMPLE_SUB_DIR = 'another/directory'
EXAMPLE_FILE = 'my_file'
EXAMPLE_FILE_EXT = '.txt'

EXAMPLE_ISSUE = datetime(1970, 10, 3, 12, tzinfo=UTC)  # a.k.a. issued at
EXAMPLE_VALID = datetime(1970, 10, 3, 14, tzinfo=UTC)  # a.k.a. valid until
EXAMPLE_LEAD = TimeDelta(EXAMPLE_VALID - EXAMPLE_ISSUE)  # a.k.a. duration of time that issue lasts
EXAMPLE_FULL_PATH = '~/blend.19701003/12/core/blend.t12z.core.f002.co.grib2.idx'


@fixture
def local_path_builder() -> PathBuilder:
    # create example Pa†hBuilder instance using test strings
    return PathBuilder(EXAMPLE_BASE_DIR, EXAMPLE_SUB_DIR, EXAMPLE_FILE, EXAMPLE_FILE_EXT)


@fixture
def path_builder() -> PathBuilder:
    subdirectory_pattern = (
        'blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/core/'
    )
    file_base_pattern = 'blend.t{issue.hour:02d}z.core.f{lead.hour:03d}.co'
    return PathBuilder('~', subdirectory_pattern, file_base_pattern, 'grib2.idx')


@fixture
def path_builder_with_region() -> PathBuilder:
    subdirectory_pattern = (
        'blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/core/'
    )
    file_base_pattern = 'blend.t{issue.hour:02d}z.core.f{lead.hour:03d}.{region:2s}'
    return PathBuilder('~', subdirectory_pattern, file_base_pattern, 'grib2.idx')


def test_from_dir_filename_creates_valid_pathbuilder():
    directory = './test_directory'
    filename = 'some_file.txt'
    path_builder = PathBuilder.from_dir_filename(directory, filename)

    assert isinstance(path_builder, PathBuilder)
    assert path_builder._basedir == directory
    assert path_builder._file_ext == ''


def test_from_path_creates_valid_pathbuilder():
    base_dir = './test_directory'
    path_builder = PathBuilder.from_path(f'{base_dir}/some_file.txt')

    assert isinstance(path_builder, PathBuilder)
    assert path_builder._basedir == base_dir
    assert path_builder._file_base == base_dir
    assert path_builder._file_ext == ''


def test_dir_fmt(local_path_builder: PathBuilder):
    assert local_path_builder.dir_fmt == f'{EXAMPLE_BASE_DIR}/{EXAMPLE_SUB_DIR}'


def test_filename_fmt(local_path_builder: PathBuilder):
    assert local_path_builder.filename_fmt == f'{EXAMPLE_FILE}{EXAMPLE_FILE_EXT}'


def test_file_ext(local_path_builder: PathBuilder):
    assert local_path_builder.file_ext == EXAMPLE_FILE_EXT


def test_path_fmt(local_path_builder: PathBuilder):
    assert local_path_builder.path_fmt == (
        f'{EXAMPLE_BASE_DIR}/{EXAMPLE_SUB_DIR}/{EXAMPLE_FILE}{EXAMPLE_FILE_EXT}'
    )


def test_build_path_with_region(path_builder_with_region: PathBuilder):
    region = 'co'
    result = path_builder_with_region.build_path(issue=EXAMPLE_ISSUE,
                                                 lead=EXAMPLE_LEAD,
                                                 region=region)
    print(result)
    result_dict = path_builder_with_region.parse_path(result)
    print(result_dict)
    assert result_dict['issue'] == EXAMPLE_ISSUE
    assert result_dict['lead'] == EXAMPLE_LEAD
    assert result_dict['region'] == region

    # if region is more than 2 chars, ValueError will be raised
    with raises(ValueError):
        result = path_builder_with_region.build_path(issue=EXAMPLE_ISSUE,
                                                     lead=EXAMPLE_LEAD,
                                                     region='conus')

    # if lead needs more than 3 chars to be represented, ValueError will be raised
    with raises(ValueError):
        result = path_builder_with_region.build_path(issue=EXAMPLE_ISSUE,
                                                     lead=EXAMPLE_LEAD*1000,
                                                     region='co')

    # if a required variable (region) is not provided, KeyError will be raised
    with raises(KeyError):
        result = path_builder_with_region.build_path(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD)

    assert False


def test_build_dir_gets_issue_valid_and_lead(path_builder: PathBuilder):
    result = path_builder.build_dir(issue=EXAMPLE_ISSUE)
    assert result == '~/blend.19701003/12/core/'


def test_build_dir_fails_without_issue(path_builder: PathBuilder):
    result = path_builder.build_dir(issue=None)
    assert result is None


def test_build_filename(path_builder: PathBuilder):
    result_filename = path_builder.build_filename(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD)
    assert result_filename == 'blend.t12z.core.f002.co.grib2.idx'


def test_build_path(path_builder: PathBuilder):
    result_filepath = path_builder.build_path(issue=EXAMPLE_ISSUE, valid=EXAMPLE_VALID)
    assert result_filepath == '~/blend.19701003/12/core/blend.t12z.core.f002.co.grib2.idx'


def test_parse_dir(path_builder: PathBuilder):
    result_dict = path_builder.parse_dir(EXAMPLE_FULL_PATH)

    assert result_dict.keys() != []
    assert result_dict['issue.year'] == 1970
    assert result_dict['issue.day'] == 3


def test_parse_filename(path_builder: PathBuilder):
    result_dict = path_builder.parse_filename(EXAMPLE_FULL_PATH)
    assert result_dict.keys() != []
    assert result_dict['lead.hour'] == 2


def test_get_issue(path_builder: PathBuilder):
    actual_issue: datetime = path_builder.get_issue(EXAMPLE_FULL_PATH)
    assert actual_issue == EXAMPLE_ISSUE


def test_get_valid_from_issue_and_lead(path_builder: PathBuilder):
    # verify valid timestamp gets successfully constructed based on issue & lead embedded into path
    result_valid: datetime = path_builder.get_valid(EXAMPLE_FULL_PATH)
    assert result_valid is not None
    assert result_valid == EXAMPLE_VALID


def test_get_valid_returns_none_when_issue_or_lead_failed(path_builder: PathBuilder):
    path_with_invalid_lead = '~/blend.19701003/12/core/blend.t12z.core.f000.co.grib2.idx'
    result_valid = path_builder.get_valid(path_with_invalid_lead)

    assert result_valid is None


# static methods
def test_get_issue_from_time_args(path_builder: PathBuilder):
    parsed_dict = path_builder.parse_path(EXAMPLE_FULL_PATH)
    issue_result = PathBuilder.get_issue_from_time_args(parsed_args=parsed_dict)

    assert issue_result == EXAMPLE_ISSUE


def test_get_issue_returns_none_if_args_empty():
    issue_result = PathBuilder.get_issue_from_time_args({})
    assert issue_result is None


def test_get_valid_from_time_args():
    parsed_dict = {}
    parsed_dict['valid.year'] = 1970
    parsed_dict['valid.month'] = 10
    parsed_dict['valid.day'] = 3
    parsed_dict['valid.hour'] = 14

    valid_result = PathBuilder.get_valid_from_time_args(parsed_dict)
    assert valid_result == EXAMPLE_VALID


def test_get_valid_returns_none_if_args_empty():
    valid_result = PathBuilder.get_valid_from_time_args({})
    assert valid_result is None


def test_get_valid_from_time_args_calculates_based_on_lead(path_builder: PathBuilder):
    parsed_dict = path_builder.parse_path(EXAMPLE_FULL_PATH)
    result_valid: datetime = PathBuilder.get_valid_from_time_args(parsed_args=parsed_dict)
    assert result_valid == EXAMPLE_VALID


def test_get_lead_from_time_args(path_builder: PathBuilder):
    parsed_dict = path_builder.parse_path(EXAMPLE_FULL_PATH)
    lead_result: timedelta = PathBuilder.get_lead_from_time_args(parsed_dict)
    assert lead_result.seconds == EXAMPLE_LEAD.minute * 60


def test_calculate_issue_from_valid_and_lead():
    parsed_dict = {
        'valid.year': 1970,
        'valid.month': 10,
        'valid.day': 3,
        'valid.hour': 14,
        'lead.hour': 2
    }

    result_issue = PathBuilder.get_issue_from_time_args(parsed_args=parsed_dict)
    assert result_issue == EXAMPLE_ISSUE

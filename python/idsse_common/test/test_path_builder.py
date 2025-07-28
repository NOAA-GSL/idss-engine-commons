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

from datetime import datetime, UTC
from pytest import fixture, raises

from idsse.common.path_builder import TimeDelta, PathBuilder

# properties
EXAMPLE_BASE_DIR = "./some/directory"
EXAMPLE_SUB_DIR = "another/directory"
EXAMPLE_FILE = "my_file"
EXAMPLE_FILE_EXT = ".txt"

EXAMPLE_ISSUE = datetime(1970, 10, 3, 12, tzinfo=UTC)  # a.k.a. issued at
EXAMPLE_VALID = datetime(1970, 10, 3, 14, tzinfo=UTC)  # a.k.a. valid until
EXAMPLE_LEAD = TimeDelta(EXAMPLE_VALID - EXAMPLE_ISSUE)  # a.k.a. duration of time that issue lasts
EXAMPLE_FULL_PATH = "~/blend.19701003/12/core/blend.t12z.core.f002.co.grib2.idx"


@fixture
def local_path_builder() -> PathBuilder:
    # create example Pa†hBuilder instance using test strings
    return PathBuilder(EXAMPLE_BASE_DIR, EXAMPLE_SUB_DIR, EXAMPLE_FILE, EXAMPLE_FILE_EXT)


@fixture
def path_builder() -> PathBuilder:
    return PathBuilder(
        "~",
        subdir="blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/core/",
        file_base="blend.t{issue.hour:02d}z.core.f{lead.hour:03d}.co",
        file_ext="grib2.idx",
    )


@fixture
def path_builder_region() -> PathBuilder:
    return PathBuilder(
        "~",
        subdir="blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/core/",
        file_base="blend.t{issue.hour:02d}z.core.f{lead.hour:03d}.{region:2s}",
        file_ext="grib2.idx",
    )


@fixture
def path_builder_leafdir() -> PathBuilder:
    return PathBuilder(
        "~",
        subdir=(
            # TODO: do we need a `:s` arg added to leafdir? True Python `Template` doesn't need it
            "blend.{issue.year:04d}{issue.month:02d}{issue.day:02d}/{issue.hour:02d}/{leafdir}/"
        ),
        file_base="blend.t{issue.hour:02d}z.{leafdir}.f{lead.hour:03d}.{region:2s}",
        file_ext="grib2.idx",
    )


def test_from_dir_filename_creates_valid_path_builder():
    directory = "./test_directory"
    filename = "some_file.txt"
    path_builder = PathBuilder.from_dir_filename(directory, filename)

    assert isinstance(path_builder, PathBuilder)
    assert path_builder.base_dir == directory
    assert path_builder.file_ext == ".txt"


def test_from_path_creates_valid_path_builder():
    base_dir = "./test_directory"
    filename = "some_file.txt"
    path_builder = PathBuilder.from_path(f"{base_dir}/{filename}")
    assert isinstance(path_builder, PathBuilder)
    assert path_builder.base_dir == base_dir
    assert path_builder.file_base == filename
    assert path_builder.file_ext == ".txt"


def test_dir_fmt(local_path_builder: PathBuilder):
    assert local_path_builder.dir_fmt == f"{EXAMPLE_BASE_DIR}/{EXAMPLE_SUB_DIR}"


def test_filename_fmt(local_path_builder: PathBuilder):
    assert local_path_builder.filename_fmt == f"{EXAMPLE_FILE}{EXAMPLE_FILE_EXT}"


def test_file_ext(local_path_builder: PathBuilder):
    assert local_path_builder.file_ext == EXAMPLE_FILE_EXT


def test_path_fmt(local_path_builder: PathBuilder):
    assert local_path_builder.path_fmt == (
        f"{EXAMPLE_BASE_DIR}/{EXAMPLE_SUB_DIR}/{EXAMPLE_FILE}{EXAMPLE_FILE_EXT}"
    )


def test_build_dir_gets_issue_valid_and_lead(path_builder: PathBuilder):
    result = path_builder.build_dir(issue=EXAMPLE_ISSUE)
    assert result == "~/blend.19701003/12/core/"


def test_build_dir_fails_without_issue(path_builder: PathBuilder):
    result = path_builder.build_dir(issue=None)
    assert result is None


def test_build_filename(path_builder: PathBuilder):
    result_filename = path_builder.build_filename(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD)
    assert result_filename == "blend.t12z.core.f002.co.grib2.idx"


def test_build_path(path_builder: PathBuilder):
    result_filepath = path_builder.build_path(issue=EXAMPLE_ISSUE, valid=EXAMPLE_VALID)
    assert result_filepath == "~/blend.19701003/12/core/blend.t12z.core.f002.co.grib2.idx"


def test_build_path_leafdir(path_builder_leafdir: PathBuilder):
    result_filepath = path_builder_leafdir.build_path(
        issue=EXAMPLE_ISSUE, valid=EXAMPLE_VALID, leafdir="leaf"
    )
    assert result_filepath == "~/blend.19701003/12/leaf/blend.t12z.leaf.f002.co.grib2.idx"


def test_build_path_with_invalid_lead(path_builder: PathBuilder):
    # if lead needs more than 3 chars to be represented, ValueError will be raised
    with raises(ValueError):
        path_builder.build_path(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD * 1000)


def test_build_path_with_region(path_builder_region: PathBuilder):
    region = "co"
    result = path_builder_region.build_path(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD, region=region)
    result_dict = path_builder_region.parse_path(result)
    assert result_dict["issue"] == EXAMPLE_ISSUE
    assert result_dict["lead"] == EXAMPLE_LEAD
    assert result_dict["region"] == region


def test_build_path_with_invalid_region(path_builder_region: PathBuilder):
    # if region is more than 2 chars, ValueError will be raised
    with raises(ValueError):
        path_builder_region.build_path(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD, region="conus")


def test_build_path_with_required_but_missing_region(path_builder_region: PathBuilder):
    # if a required variable (region) is not provided, KeyError will be raised
    with raises(KeyError):
        path_builder_region.build_path(issue=EXAMPLE_ISSUE, lead=EXAMPLE_LEAD)


def test_parse_dir(path_builder: PathBuilder):
    result_dict = path_builder.parse_dir(EXAMPLE_FULL_PATH)

    assert result_dict.keys() != []
    assert result_dict["issue.year"] == 1970
    assert result_dict["issue.day"] == 3


def test_parse_filename(path_builder: PathBuilder):
    result_dict = path_builder.parse_filename(EXAMPLE_FULL_PATH)
    assert result_dict.keys() != []
    assert result_dict["lead.hour"] == 2


def test_get_issue(path_builder: PathBuilder):
    actual_issue: datetime = path_builder.get_issue(EXAMPLE_FULL_PATH)
    assert actual_issue == EXAMPLE_ISSUE


def test_get_valid_from_issue_and_lead(path_builder: PathBuilder):
    # verify valid timestamp gets successfully constructed based on issue & lead embedded into path
    result_valid: datetime = path_builder.get_valid(EXAMPLE_FULL_PATH)
    assert result_valid is not None
    assert result_valid == EXAMPLE_VALID


def test_get_valid_returns_none_when_issue_or_lead_failed(path_builder: PathBuilder):
    path_with_invalid_lead = "~/blend.19701003/12/core/blend.t12z.core.f000.co.grib2.idx"
    result_valid = path_builder.get_valid(path_with_invalid_lead)

    assert result_valid is None

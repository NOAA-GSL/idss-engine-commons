"""Test suite for netcdf_io.py"""

# ----------------------------------------------------------------------------------
# Created on Mon May 1 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2025 Colorado State University. All rights reserved.             (2)
#
# Contributors:
#     Geary J Layne     (1)
#     Mackenzie Grimes  (2)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access,unused-argument

import os
from datetime import datetime
from typing import NamedTuple

from dateutil.parser import parse as dt_parse
from pytest import approx, fail, fixture
from numpy import ndarray

from idsse.common.sci.netcdf_io import read_netcdf, read_netcdf_global_attrs, write_netcdf
from idsse.common.utils import FileBasedLock

# test data
EXAMPLE_NETCDF_FILEPATH = f"{os.path.dirname(__file__)}/../resources/gridstore55657865.nc"

EXAMPLE_ATTRIBUTES = {
    "product": "NBM.AWS.GRIB",
    "field": "TEMP",
    "valid_dt": "2022-11-11 17:00:00+00:00",
    "issue_dt": "2022-11-11 14:00:00+00:00",
    "task": "data_task",
    "region": "CONUS",
    "units": "Fahrenheit",
    "proj_name": "NBM",
    "proj_spec": "+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +a=6371200",
    "grid_spec": "+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766",
    "data_key": "NBM.AWS.GRIB:CO:TEMP::Fahrenheit::20221111140000.20221111170000",
    "data_name": "Temperature: 2m",
    "data_loc": "arn:aws:s3:::noaa-nbm-grib2-pds:",
    "data_order": "latitude,longitude",
}

EXAMPLE_PROD_KEY = (
    "product:NBM.AWS.GRIB-field:TEMP-issue:20221111140000-valid:20221112000000-units:Fahrenheit"
)


def is_attributes_equal(actual: dict, expected: dict) -> bool:
    """Utility function to check if two attributes dictionaries match"""
    if not len(actual) == len(expected):
        return False

    # each attribute should match expected by key,
    # except any ISO strings may have been transformed to Python datetimes
    for key, value in actual.items():
        expected_value = expected[key]
        if isinstance(value, datetime):
            # if expected value is not datetime, transform to datetime before comparison
            if isinstance(expected_value, str):
                expected_value = dt_parse(expected_value)
            if value != expected_value:  # now comparing two datetimes together
                return False

        if value != expected_value:
            return False

    return True


# pytest fixtures
@fixture
def netcdf_lock() -> FileBasedLock:
    """Hack to avoid netCDF4 single-thread limitations; no two unit test can use the netCDF4
    read/write NetCDFs (at any file path) at the same time
    """
    # pylint: disable=duplicate-code
    global_lock_file = os.path.join(os.path.dirname(__file__), "..", "resources", "netcdf4")
    return FileBasedLock(global_lock_file, max_age=15)


@fixture
def example_netcdf_data(netcdf_lock) -> tuple[dict[str, any], ndarray]:
    # file lock protects against other unit tests having NetCDF file open (HDF throws OSError 101)
    with netcdf_lock:
        result = read_netcdf(EXAMPLE_NETCDF_FILEPATH)
    return result


def test_read_netcdf_global_attrs(netcdf_lock):
    with netcdf_lock:
        attrs = read_netcdf_global_attrs(EXAMPLE_NETCDF_FILEPATH)

    # attrs should be same as input attrs
    assert is_attributes_equal(attrs, EXAMPLE_ATTRIBUTES)


def test_read_netcdf_global_attrs_with_h5nc():
    attrs = read_netcdf_global_attrs(EXAMPLE_NETCDF_FILEPATH, use_h5_lib=True)

    # attrs should be same as input attrs, except any ISO strings transformed to Python datetimes
    assert is_attributes_equal(attrs, EXAMPLE_ATTRIBUTES)


def test_read_netcdf(example_netcdf_data: tuple[dict, ndarray]):
    attrs, grid = example_netcdf_data

    assert grid.shape == (1597, 2345)
    y_max, x_max = grid.shape
    assert grid[0, 0] == approx(72.80599)
    assert grid[round(y_max / 2), round(x_max / 2)] == approx(26.005991)
    assert grid[y_max - 1, x_max - 1] == approx(15.925991)
    assert is_attributes_equal(attrs, EXAMPLE_ATTRIBUTES)


def test_read_netcdf_with_h5nc():
    attrs, grid = read_netcdf(EXAMPLE_NETCDF_FILEPATH, use_h5_lib=True)

    assert grid.shape == (1597, 2345)
    y_max, x_max = grid.shape
    assert grid[0, 0] == approx(72.80599)
    assert grid[round(y_max / 2), round(x_max / 2)] == approx(26.005991)
    assert grid[y_max - 1, x_max - 1] == approx(15.925991)
    assert is_attributes_equal(attrs, EXAMPLE_ATTRIBUTES)


@fixture
def destination_nc_file() -> str:
    parent_dir = os.path.abspath("./tmp")
    file = "test_netcdf_file.nc"
    filepath = f"{parent_dir}/{file}"
    # create test file dir if needed
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)
    # cleanup existing test file if needed
    if os.path.exists(filepath):
        os.remove(filepath)

    yield filepath

    # cleanup created netcdf file and its parent dir
    if os.path.exists(filepath):
        os.remove(filepath)
    if os.path.exists(parent_dir):
        os.rmdir(parent_dir)


def test_read_and_write_netcdf(
    example_netcdf_data: tuple[dict[str, any], ndarray], destination_nc_file: str, netcdf_lock
):
    attrs, grid = example_netcdf_data
    attrs["prodKey"] = EXAMPLE_PROD_KEY
    attrs["prodSource"] = attrs["product"]

    # verify write_netcdf functionality
    with netcdf_lock:
        written_filepath = write_netcdf(attrs, grid, destination_nc_file)

    assert written_filepath == destination_nc_file
    assert os.path.exists(destination_nc_file)

    # verify read_netcdf functionality
    with netcdf_lock:
        new_file_attrs, new_file_grid = read_netcdf(written_filepath)

    assert is_attributes_equal(new_file_attrs, attrs)
    assert new_file_grid[123][321] == grid[123][321]
    assert is_attributes_equal(new_file_attrs, attrs)


def test_read_and_write_netcdf_with_h5(
    example_netcdf_data: tuple[dict[str, any], ndarray], destination_nc_file: str
):
    attrs, grid = example_netcdf_data
    attrs["prodKey"] = EXAMPLE_PROD_KEY
    attrs["prodSource"] = attrs["product"]

    # verify write_netcdf_with_h5nc functionality
    written_filepath = write_netcdf(attrs, grid, destination_nc_file, use_h5_lib=True)

    assert written_filepath == destination_nc_file

    # verify read_netcdf with h5nc functionality
    new_file_attrs, new_file_grid = read_netcdf(written_filepath, use_h5_lib=True)

    assert new_file_grid[123][321] == grid[123][321]
    assert is_attributes_equal(new_file_attrs, attrs)


def test_write_netcdf_nonstring_attrs(
    example_netcdf_data: tuple[dict[str, any], ndarray], destination_nc_file: str
):
    in_attrs, grid = example_netcdf_data
    SpecialType = NamedTuple("SpecialType", [("field", str), ("data_type", str)])
    # create non-string attribute of weird type
    in_attrs["field"] = SpecialType(field="temperature", data_type="prctl_p025")

    try:
        # verify write_netcdf successfully writes non-string attrs (they shouldn't be anyway)
        _ = write_netcdf(in_attrs, grid, destination_nc_file, use_h5_lib=True)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        fail(f"Unable to write NetCDF to {destination_nc_file} due to exception: {str(exc)}")

    out_attrs = read_netcdf_global_attrs(destination_nc_file, use_h5_lib=True)
    for value in out_attrs.values():
        assert isinstance(value, (str, datetime))

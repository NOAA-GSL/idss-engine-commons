"""Test suite for netcdf_io.py"""
# --------------------------------------------------------------------------------
# Created on Mon May 1 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# --------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,protected-access,unused-argument

import os

from pytest import fixture, approx
from numpy import ndarray

from idsse.common.sci.netcdf_io import read_netcdf, read_netcdf_global_attrs, write_netcdf


# test data
EXAMPLE_NETCDF_FILEPATH = f'{os.path.dirname(__file__)}/../resources/gridstore55657865.nc'

EXAMPLE_ATTRIBUTES = {
    'product': 'NBM.AWS.GRIB',
    'field': 'TEMP',
    'valid_dt': '2022-11-11 17:00:00+00:00',
    'issue_dt': '2022-11-11 14:00:00+00:00',
    'task': 'data_task',
    'region': 'CONUS',
    'units': 'Fahrenheit',
    'proj_name': 'NBM',
    'proj_spec': '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +a=6371200',
    'grid_spec': '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766',
    'data_key': 'NBM.AWS.GRIB:CO:TEMP::Fahrenheit::20221111140000.20221111170000',
    'data_name': 'Temperature: 2m',
    'data_loc': 'arn:aws:s3:::noaa-nbm-grib2-pds:',
    'data_order': 'latitude,longitude'
}

EXAMPLE_PROD_KEY = (
    'product:NBM.AWS.GRIB-field:TEMP-issue:20221111140000-valid:20221112000000-units:Fahrenheit'
)


# pytest fixtures
@fixture
def example_netcdf_data() -> tuple[dict[str, any], ndarray]:
    return read_netcdf(EXAMPLE_NETCDF_FILEPATH)


# tests
def test_read_netcdf_global_attrs():
    attrs = read_netcdf_global_attrs(EXAMPLE_NETCDF_FILEPATH)

    assert len(attrs) == len(EXAMPLE_ATTRIBUTES)
    assert attrs == EXAMPLE_ATTRIBUTES


def test_read_netcdf(example_netcdf_data: tuple[dict[str, any], ndarray]):
    attrs, grid = example_netcdf_data

    assert grid.shape == (1597, 2345)
    y_max, x_max = grid.shape

    assert grid[0, 0] == approx(72.80599)
    assert grid[round(y_max / 2), round(x_max / 2)] == approx(26.005991)
    assert grid[y_max - 1, x_max - 1] == approx(15.925991)

    assert attrs == EXAMPLE_ATTRIBUTES


def test_read_and_write_netcdf(example_netcdf_data: tuple[dict[str, any], ndarray]):
    # cleanup existing test file if needed
    temp_netcdf_filepath = './tmp/test_netcdf_file.nc'
    if os.path.exists(temp_netcdf_filepath):
        os.remove(temp_netcdf_filepath)

    attrs, grid = example_netcdf_data

    # verify write_netcdf functionality
    attrs['prodKey'] = EXAMPLE_PROD_KEY
    attrs['prodSource'] = attrs['product']
    written_filepath = write_netcdf(attrs, grid, temp_netcdf_filepath)
    assert written_filepath == temp_netcdf_filepath
    assert os.path.exists(temp_netcdf_filepath)

    new_file_attrs, new_file_grid = read_netcdf(written_filepath)
    assert new_file_attrs == attrs
    assert new_file_grid[123][321] == grid[123][321]

    # cleanup created netcdf file
    os.remove(temp_netcdf_filepath)


def test_read_and_write_netcdf_with_h5nc(example_netcdf_data: tuple[dict[str, any], ndarray]):
    # create h5nc file
    temp_netcdf_h5_filepath = './tmp/test_netcdf_h5_file.nc'
    if os.path.exists(temp_netcdf_h5_filepath):
        os.remove(temp_netcdf_h5_filepath)

    attrs, grid = example_netcdf_data

    # verify write_netcdf_with_h5nc functionality
    attrs['prodKey'] = EXAMPLE_PROD_KEY
    attrs['prodSource'] = attrs['product']
    written_filepath = write_netcdf(attrs, grid, temp_netcdf_h5_filepath, use_h5_lib=True)
    assert written_filepath == temp_netcdf_h5_filepath

    # Don't verify h5 attrs for now; they are some custom h5py type and aren't easy to access
    _, new_file_grid = read_netcdf(written_filepath, use_h5_lib=True)
    assert new_file_grid[123][321] == grid[123][321]

    # cleanup created netcdf h5 file
    os.remove(temp_netcdf_h5_filepath)

"""Test suite for grid_proj.py"""
# ----------------------------------------------------------------------------------
# Created on Wed Aug 2 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Mackenzie Grimes (2)
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,protected-access
# cspell:ignore pyproj

from typing import Tuple, List

import numpy as np
from pytest import approx, fixture, raises

from idsse.common.sci.grid_proj import GridProj
from idsse.common.utils import round_, RoundingMethod


# example data
EXAMPLE_PROJ_SPEC = '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +a=6371200'
EXAMPLE_GRID_SPEC = '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766'

PROJ_SPEC_WITH_OFFSET = (
    '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 '
    '+x_0=3275807.350733357 +y_0=260554.63043505285 +a=6371200'
)
GRID_SPEC_WITHOUT_LOWER_LEFT = '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597'

WIDTH = 2345
HEIGHT = 1597

EXAMPLE_PIXELS: List[Tuple[int, int]] = [
    (0, 0),
    (0, 1),
    (2000, 1500)
]
EXAMPLE_LON_LAT = [
    (-126.2766, 19.229),
    (-126.28210431967231, 19.25112362717893),
    (-71.02234126905036, 54.014077268729)
]
EXAMPLE_CRS = [
    (-3271151.6058371724, -263793.7334645616),
    (-3271151.6058371724, -261254.03046456157),
    (1808254.3941628276, 3545760.7665354386)
]


# utility to roughly compare tuples of floats with less floating point precision
def approx_tuple(values: Tuple[float, float]) -> Tuple:
    return (approx(values[0]), approx(values[1]))


# fixtures
@fixture
def grid_proj() -> GridProj:
    return GridProj.from_proj_grid_spec(EXAMPLE_PROJ_SPEC, EXAMPLE_GRID_SPEC)


# test class methods
def test_from_proj_grid_spec(grid_proj: GridProj):
    assert isinstance(grid_proj, GridProj)

    assert (grid_proj._x_offset, grid_proj._y_offset) == approx_tuple(EXAMPLE_CRS[0])
    assert grid_proj._h == 1597
    assert grid_proj._w == 2345
    assert grid_proj._dx == approx(2539.703)
    assert grid_proj._dy == grid_proj._dx

    t = grid_proj._trans
    assert t.source_crs is not None and t.source_crs.type_name == 'Geographic 2D CRS'
    assert t.target_crs is not None and t.target_crs.type_name == 'Projected CRS'


def test_from_proj_grid_spec_with_offset():
    proj_with_offset = GridProj.from_proj_grid_spec(PROJ_SPEC_WITH_OFFSET,
                                                    GRID_SPEC_WITHOUT_LOWER_LEFT)

    proj_xy = proj_with_offset.map_pixel_to_geo(*EXAMPLE_PIXELS[0])
    assert proj_xy == approx_tuple((-126.32657866, 19.247681536))


# test properties
def test_get_width(grid_proj: GridProj):
    assert grid_proj.width == WIDTH


def test_get_height(grid_proj: GridProj):
    assert grid_proj.height == HEIGHT


def test_get_shape(grid_proj: GridProj):
    assert grid_proj.shape == (WIDTH, HEIGHT)


# test flips
def test_fliplr(grid_proj: GridProj):
    lower_left_lon_lat = grid_proj.map_pixel_to_geo(0, 0)
    grid_proj.fliplr()
    assert grid_proj.map_pixel_to_geo(grid_proj.width, 0) == lower_left_lon_lat


def test_flipud(grid_proj: GridProj):
    lower_left_lon_lat = grid_proj.map_pixel_to_geo(0, 0)
    grid_proj.flipud()
    assert grid_proj.map_pixel_to_geo(0, grid_proj.height) == lower_left_lon_lat


def test_flip_both_lr_ud(grid_proj: GridProj):
    lower_left_lon_lat = grid_proj.map_pixel_to_geo(0, 0)
    grid_proj.flip()
    assert grid_proj.map_pixel_to_geo(grid_proj.width, grid_proj.height) == lower_left_lon_lat


# transformation methods testing
def test_map_crs_to_pixel_round(grid_proj: GridProj):
    for index, crs_xy in enumerate(EXAMPLE_CRS):
        pixel_xy = grid_proj.map_crs_to_pixel(
            *crs_xy,
            rounding=RoundingMethod.ROUND
        )
        assert pixel_xy == EXAMPLE_PIXELS[index]


def test_map_crs_to_pixel_floor(grid_proj: GridProj):
    for index, crs_xy in enumerate(EXAMPLE_CRS):
        i, j = grid_proj.map_crs_to_pixel(
            *crs_xy,
            rounding=RoundingMethod.FLOOR
        )
        # due to math imprecision internal to pyproj.transform(), some test results are a bit
        # unpredictable. E.g. returns 0.999994, which floors to 0, when expected pixel value is 1
        assert (approx(i, abs=1), approx(j, abs=1)) == EXAMPLE_PIXELS[index]


def test_map_geo_to_crs(grid_proj: GridProj):
    for index, lon_lat in enumerate(EXAMPLE_LON_LAT):
        geo_xy = grid_proj.map_geo_to_crs(*lon_lat)
        assert geo_xy == approx_tuple(EXAMPLE_CRS[index])


def test_map_pixel_to_crs(grid_proj: GridProj):
    for index, pixel in enumerate(EXAMPLE_PIXELS):
        geo_x, geo_y = grid_proj.map_pixel_to_crs(*pixel)
        assert (geo_x, geo_y) == approx_tuple(EXAMPLE_CRS[index])


def test_map_pixel_to_geo(grid_proj: GridProj):
    for index, pixel in enumerate(EXAMPLE_PIXELS):
        proj_x, proj_y = grid_proj.map_pixel_to_geo(*pixel)
        assert (proj_x, proj_y) == approx_tuple(EXAMPLE_LON_LAT[index])


def test_map_crs_to_geo(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_CRS):
        proj_x, proj_y = grid_proj.map_crs_to_geo(*geo)
        assert (proj_x, proj_y) == approx_tuple(EXAMPLE_LON_LAT[index])


def test_crs_to_pixel_no_rounding(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_CRS):
        i, j = grid_proj.map_crs_to_pixel(*geo)
        # round result, which will not be precisely the integer that was passed
        assert (round_(i, 6), round_(j, 6)) == EXAMPLE_PIXELS[index]


def test_crs_to_pixel_floor(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_CRS):
        i, j = grid_proj.map_crs_to_pixel(*geo)
        assert (round_(i), round_(j)) == EXAMPLE_PIXELS[index]

        floor_ij = grid_proj.map_crs_to_pixel(*geo, rounding=RoundingMethod.FLOOR)
        assert (
            round_(i, rounding=RoundingMethod.FLOOR), round_(j, rounding=RoundingMethod.FLOOR)
        ) == floor_ij


def test_crs_to_pixel_round(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_CRS):
        i, j = grid_proj.map_crs_to_pixel(*geo, rounding=RoundingMethod.ROUND)
        assert (i, j) == EXAMPLE_PIXELS[index]


def test_crs_to_pixel_round_str(grid_proj: GridProj):
    i, j = grid_proj.map_crs_to_pixel(*EXAMPLE_CRS[0], rounding='round')
    assert (i, j) == EXAMPLE_PIXELS[0]

    i, j = grid_proj.map_crs_to_pixel(*EXAMPLE_CRS[1], rounding='ROUND')
    assert (i, j) == EXAMPLE_PIXELS[1]


def test_compound_transformations_stay_consistent(grid_proj: GridProj):
    # start with pixel, convert to projection
    initial_pixel = (EXAMPLE_PIXELS[2][0], EXAMPLE_PIXELS[2][1])
    proj_x, proj_y = grid_proj.map_pixel_to_geo(*initial_pixel)
    initial_geo = (proj_x, proj_y)

    # convert projection to geographic coordinates
    geo_x, geo_y = grid_proj.map_geo_to_crs(proj_x, proj_y)
    initial_crs = geo_x, geo_y

    # convert geographic coordinates back to pixel, full circle, and data should be unchanged
    pixel_x, pixel_y = grid_proj.map_crs_to_pixel(geo_x, geo_y)
    assert (round_(pixel_x, 6), round_(pixel_y, 6)) == initial_pixel

    # convert pixel back to geographic coordinates
    geo_x, geo_y = grid_proj.map_pixel_to_crs(pixel_x, pixel_y)
    assert (geo_x, geo_y) == approx_tuple(initial_crs)

    # convert geographic coordinates back to projection
    proj_x, proj_y = grid_proj.map_crs_to_geo(geo_x, geo_y)
    assert (proj_x, proj_y) == approx_tuple(initial_geo)


def test_geo_to_pixel_list(grid_proj: GridProj):
    # split example list of tuples into: list of lats and list of lons
    lon_lat_arrays: tuple[list[float]] = tuple(zip(*EXAMPLE_LON_LAT))

    # pass full arrays to map_geo_to_pixel
    pixel_arrays = grid_proj.map_geo_to_pixel(*lon_lat_arrays, rounding=RoundingMethod.ROUND)

    expected_xs, expected_ys = list(zip(*EXAMPLE_PIXELS))
    assert pixel_arrays[0] == expected_xs
    assert pixel_arrays[1] == expected_ys


def test_pixel_to_geo_numpy_array(grid_proj: GridProj):
    i_array, j_array = list(zip(*EXAMPLE_PIXELS))

    # pass full numpy arrays to map_pixel_to_geo
    i_numpy_array = np.array(i_array)
    j_numpy_array = np.array(j_array)
    geo_arrays = grid_proj.map_pixel_to_geo(i_numpy_array, j_numpy_array)

    expected_geos = tuple(np.array(values) for values in zip(*EXAMPLE_LON_LAT))

    # both x and y coordinate arrays should be numpy arrays
    assert all(isinstance(arr, np.ndarray) for arr in geo_arrays)
    np.testing.assert_almost_equal(geo_arrays, expected_geos)


def test_geo_to_pixel_numpy_array(grid_proj: GridProj):
    x_values, y_values = list(zip(*EXAMPLE_LON_LAT))
    pixel_arrays = grid_proj.map_geo_to_pixel(
        np.array(x_values), np.array(y_values), rounding=RoundingMethod.ROUND
    )

    expected_arrays = np.array(list(zip(*EXAMPLE_PIXELS)))

    # both x and y coordinate arrays returned should be numpy arrays
    assert all(isinstance(arr, np.ndarray) for arr in pixel_arrays)
    np.testing.assert_array_equal(pixel_arrays, expected_arrays)


def test_unbalanced_pixel_or_crs_arrays_fail_to_transform(grid_proj: GridProj):
    with raises(TypeError) as exc:
        bad_pixel = (1.0, [1.0, 2.0, 3.0])
        grid_proj.map_pixel_to_crs(*bad_pixel)
    assert 'Cannot transpose pixel values' in exc.value.args[0]

    with raises(TypeError) as exc:
        bad_crs = (EXAMPLE_CRS[0], EXAMPLE_CRS[1][1])
        grid_proj.map_crs_to_pixel(*bad_crs, rounding=RoundingMethod.ROUND)
    assert 'Cannot transpose CRS values' in exc.value.args[0]

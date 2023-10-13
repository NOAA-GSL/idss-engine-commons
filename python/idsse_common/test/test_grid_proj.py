"""Test suite for grid_geo.py"""
# ----------------------------------------------------------------------------------
# Created on Wed Aug 2 2023
#
# Copyright (c) 2023 Colorado State University. All rights reserved. (1)
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (2)
#
# Contributors:
#     Mackenzie Grimes (1)
#     Geary Layne (2)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,protected-access

import math
from typing import Tuple

from pytest import fixture, approx

from idsse.common.grid_proj import GridProj, RoundingMethod
from idsse.common.utils import round_half_away

# cspell:ignore pyproj


# example data
EXAMPLE_PROJ_SPEC = '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200'
EXAMPLE_GRID_SPEC = '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766'

PROJ_SPEC_WITH_OFFSET = (
    '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 '
    '+x_0=3275807.350733357 +y_0=260554.63043505285 +r=6371200'
)
GRID_SPEC_WITHOUT_LOWER_LEFT = '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597'

WIDTH = 2345
HEIGHT = 1597

EXAMPLE_PIXELS = [
    (0, 0),
    (0, 1),
    (2000, 1500)
]
EXAMPLE_LON_LAT = [
    (-126.2766, 19.229),
    (-126.28209649530142, 19.251224896946418),
    (-71.12860760432866, 54.09108720984939)
]
EXAMPLE_CRS = [
    (-3275807.350733357, -260554.63043505285),
    (-3275807.3507333556, -258014.92743505232),
    (1803598.6492666428, 3548999.8695649463)
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
    assert proj_xy == approx_tuple(EXAMPLE_LON_LAT[0])


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
def test_map_crs_to_pixel_round_half_away(grid_proj: GridProj):
    for index, crs_xy in enumerate(EXAMPLE_CRS):
        pixel_xy = grid_proj.map_crs_to_pixel(
            *crs_xy,
            rounding=RoundingMethod.ROUND
        )
        assert pixel_xy == EXAMPLE_PIXELS[index]


def test_map_crs_to_pixel_round_floor(grid_proj: GridProj):
    for index, crs_xy in enumerate(EXAMPLE_CRS):
        i, j = grid_proj.map_crs_to_pixel(
            *crs_xy,
            rounding=RoundingMethod.FLOOR
        )
        # due to math imprecision internal to pyproj.transform(), some test results are a bit
        # unpredictable. E.g. returns 0.999994 which is floored to 0, but expected pixel value is 1
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
        assert (round_half_away(i, 6), round_half_away(j, 6)) == EXAMPLE_PIXELS[index]


def test_crs_to_pixel_floor(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_CRS):
        floor_ij = grid_proj.map_crs_to_pixel(*geo, RoundingMethod.FLOOR)
        i, j = grid_proj.map_crs_to_pixel(*geo)
        assert (math.floor(i), math.floor(j)) == floor_ij
        assert (round_half_away(i), round_half_away(j)) == EXAMPLE_PIXELS[index]


def test_crs_to_pixel_round(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_CRS):
        i, j = grid_proj.map_crs_to_pixel(*geo, RoundingMethod.ROUND)
        assert (i, j) == EXAMPLE_PIXELS[index]


def test_crs_to_pixel_round_str(grid_proj: GridProj):
    i, j = grid_proj.map_crs_to_pixel(*EXAMPLE_CRS[0], 'round')
    assert (i, j) == EXAMPLE_PIXELS[0]

    i, j = grid_proj.map_crs_to_pixel(*EXAMPLE_CRS[1], 'ROUND')
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
    assert (round_half_away(pixel_x, 6), round_half_away(pixel_y, 6)) == initial_pixel

    # convert pixel back to geographic coordinates
    geo_x, geo_y = grid_proj.map_pixel_to_crs(pixel_x, pixel_y)
    assert (geo_x, geo_y) == approx_tuple(initial_crs)

    # convert geographic coordinates back to projection
    proj_x, proj_y = grid_proj.map_crs_to_geo(geo_x, geo_y)
    assert (proj_x, proj_y) == approx_tuple(initial_geo)

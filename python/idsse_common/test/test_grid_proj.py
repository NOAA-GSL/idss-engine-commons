"""Test suite for grid_proj.py"""
# --------------------------------------------------------------------------------
# Created on Wed Aug 2 2023
#
# Copyright (c) 2023 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# --------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,protected-access

from typing import Tuple

from pytest import fixture, approx

from idsse.common.grid_proj import GridProj, RoundingMethod

# example data
EXAMPLE_PROJ_SPEC = '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200'
PROJ_SPEC_WITH_OFFSET = (
    '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +x_0=3271.152832031251 '
    '+y_0=263.7934687500001 +r=6371.2, +units=km'
)
EXAMPLE_GRID_SPEC = "+dx=2.539703 +dy=2.539703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766"

EXAMPLE_PIXELS = [
    (0, 0),
    (0, 1),
    (2000, 1500)
]
EXAMPLE_PROJECTIONS = [
    (-126.2766, 19.229),
    (-126.27660549554, 19.229022224607),
    (-126.23803580508, 19.272773488997)
]
EXAMPLE_GEOS = [
    (-3275807.350733, -260554.63043505),
    (-3275807.350733, -260552.09073205),
    (-3270727.944733, -256745.07593505)
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

    assert (grid_proj._x_offset, grid_proj._y_offset) == approx_tuple(EXAMPLE_GEOS[0])
    assert grid_proj._h == 1597
    assert grid_proj._w == 2345
    assert grid_proj._dx == approx(2.539703)
    assert grid_proj._dy == grid_proj._dx

    t = grid_proj._trans
    assert t.source_crs is not None and t.source_crs.type_name == 'Geographic 2D CRS'
    assert t.target_crs is not None and t.target_crs.type_name == 'Projected CRS'


def test_from_proj_grid_spec_with_offset():
    proj_with_offset = GridProj.from_proj_grid_spec(PROJ_SPEC_WITH_OFFSET, EXAMPLE_GRID_SPEC)
    assert proj_with_offset._x_offset == approx(-3272536.1979)
    assert proj_with_offset._y_offset == approx(-260290.8369)


# transformation methods testing
def test_map_proj_to_pixel(grid_proj: GridProj):
    for index, proj in enumerate(EXAMPLE_PROJECTIONS):
        pixel_x, pixel_y = grid_proj.map_proj_to_pixel(*proj)
        assert (round(pixel_x, 6), round(pixel_y, 6)) == EXAMPLE_PIXELS[index]


def test_map_proj_to_geo(grid_proj: GridProj):
    for index, proj in enumerate(EXAMPLE_PROJECTIONS):
        geo_x, geo_y = grid_proj.map_proj_to_geo(*proj)
        assert (geo_x, geo_y) == approx_tuple(EXAMPLE_GEOS[index])


def test_map_pixel_to_geo(grid_proj: GridProj):
    for index, pixel in enumerate(EXAMPLE_PIXELS):
        geo_x, geo_y = grid_proj.map_pixel_to_geo(*pixel)
        assert (geo_x, geo_y) == approx_tuple(EXAMPLE_GEOS[index])


def test_map_pixel_to_proj(grid_proj: GridProj):
    for index, pixel in enumerate(EXAMPLE_PIXELS):
        proj_x, proj_y = grid_proj.map_pixel_to_proj(*pixel)
        assert (proj_x, proj_y) == approx_tuple(EXAMPLE_PROJECTIONS[index])


def test_map_geo_to_proj(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_GEOS):
        proj_x, proj_y = grid_proj.map_geo_to_proj(*geo)
        assert (proj_x, proj_y) == approx_tuple(EXAMPLE_PROJECTIONS[index])


def test_geo_to_pixel_no_rounding(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_GEOS):
        pixel_x, pixel_y = grid_proj.map_geo_to_pixel(*geo)
        # round result, which will not be precisely the integer that was passed
        assert (round(pixel_x, 6), round(pixel_y, 6)) == EXAMPLE_PIXELS[index]


def test_geo_to_pixel_floor(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_GEOS):
        pixel_x, pixel_y = grid_proj.map_geo_to_pixel(*geo, RoundingMethod.ROUND_FLOOR)
        assert (pixel_x, pixel_y) == EXAMPLE_PIXELS[index]


def test_geo_to_pixel_round(grid_proj: GridProj):
    for index, geo in enumerate(EXAMPLE_GEOS):
        pixel_x, pixel_y = grid_proj.map_geo_to_pixel(*geo, RoundingMethod.ROUND_HALF_UP)
        assert (pixel_x, pixel_y) == EXAMPLE_PIXELS[index]


def test_compound_tranformations_stay_consistent(grid_proj: GridProj):
    # start with pixel, convert to projection
    initial_pixel = (EXAMPLE_PIXELS[2][0], EXAMPLE_PIXELS[2][1])
    proj_x, proj_y = grid_proj.map_pixel_to_proj(*initial_pixel)
    initial_proj = (proj_x, proj_y)

    # convert projection to geographic coordinates
    geo_x, geo_y = grid_proj.map_proj_to_geo(proj_x, proj_y)
    initial_geo = geo_x, geo_y

    # convert geographic coordinates back to pixel, full circle, and data should be unchanged
    pixel_x, pixel_y = grid_proj.map_geo_to_pixel(geo_x, geo_y)
    assert (round(pixel_x, 6), round(pixel_y, 6)) == initial_pixel

    # convert pixel back to geographic coordinates
    geo_x, geo_y = grid_proj.map_pixel_to_geo(pixel_x, pixel_y)
    assert (geo_x, geo_y) == approx_tuple(initial_geo)

    # convert geographic coordinates back to projection
    proj_x, proj_y = grid_proj.map_geo_to_proj(geo_x, geo_y)
    assert (proj_x, proj_y) == approx_tuple(initial_proj)

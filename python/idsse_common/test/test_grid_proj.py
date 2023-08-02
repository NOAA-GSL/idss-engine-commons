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

from pytest import fixture, approx

from idsse.common.grid_proj import GridProj

# example data
EXAMPLE_PROJ_SPEC = '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200'
PROJ_SPEC_WITH_OFFSET = (
    '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +x_0=3271.152832031251 '
    '+y_0=263.7934687500001 +r=6371.2, +units=km'
)
EXAMPLE_GRID_SPEC = "+dx=2.539703 +dy=2.539703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766"
EXAMPLE_PROJECTION = (-126.2766, 19.229)
EXAMPLE_PIXEL = (0, 1)
EXAMPLE_GEO = (-3275807.35073, -260554.63043)


# fixtures
@fixture
def grid_proj() -> GridProj:
    return GridProj.from_proj_grid_spec(EXAMPLE_PROJ_SPEC, EXAMPLE_GRID_SPEC)


# test class methods
def test_from_proj_grid_spec(grid_proj: GridProj):
    assert isinstance(grid_proj, GridProj)

    assert grid_proj._dx == approx(2.539703)
    assert grid_proj._dy == grid_proj._dx
    assert grid_proj._x_offset == approx(-3275807.3507)
    assert grid_proj._y_offset == approx(-260554.6304)
    assert grid_proj._h == 1597
    assert grid_proj._w == 2345

    transformer = grid_proj._trans
    assert transformer.source_crs is not None
    assert transformer.source_crs.type_name == 'Geographic 2D CRS'
    assert transformer.target_crs is not None
    assert transformer.target_crs.type_name == 'Projected CRS'


def test_from_proj_grid_spec_with_offset():
    proj_with_offset = GridProj.from_proj_grid_spec(PROJ_SPEC_WITH_OFFSET, EXAMPLE_GRID_SPEC)
    assert proj_with_offset._x_offset == approx(-3272536.1979)
    assert proj_with_offset._y_offset == approx(-260290.8369)


# transformation methods testing
def test_map_proj_to_pixel(grid_proj: GridProj):
    pixel_x, pixel_y = grid_proj.map_proj_to_pixel(*EXAMPLE_PROJECTION)
    assert (pixel_x, pixel_y) == (0, 0)

    pixel_x, pixel_y = grid_proj.map_proj_to_pixel(-126.2666, 19.2333)
    assert (pixel_x, pixel_y) == (approx(448.1133842), approx(88.24123))


def test_map_proj_to_geo(grid_proj: GridProj):
    geo_x, geo_y = grid_proj.map_proj_to_geo(*EXAMPLE_PROJECTION)
    assert (geo_x, geo_y) == (approx(EXAMPLE_GEO[0]), approx(EXAMPLE_GEO[1]))

    geo_x, geo_y = grid_proj.map_proj_to_geo(-126.2666, 19.2333)
    assert (geo_x, geo_y) == (approx(-3274669.2758), approx(-260330.52389))


def test_map_pixel_to_geo(grid_proj: GridProj):
    geo_x, geo_y = grid_proj.map_pixel_to_geo(*EXAMPLE_PIXEL)
    assert (geo_x, geo_y) == (approx(-3275807.35073), approx(-260552.090732))

    geo_x, geo_y = grid_proj.map_pixel_to_geo(448.1133842, 8824124)
    assert (geo_x, geo_y) == (approx(-3274669.2758), approx(22150099.56473))


def test_map_pixel_to_proj(grid_proj: GridProj):
    proj_x, proj_y = grid_proj.map_pixel_to_proj(0, 0)
    assert (proj_x, proj_y) == (approx(EXAMPLE_PROJECTION[0]), approx(EXAMPLE_PROJECTION[1]))

    proj_x, proj_y = grid_proj.map_pixel_to_proj(2000, 1500)
    assert (proj_x, proj_y) == (approx(-126.238035), approx(19.272773))


def test_map_geo_to_proj(grid_proj: GridProj):
    proj_x, proj_y = grid_proj.map_geo_to_proj(*EXAMPLE_GEO)
    assert (proj_x, proj_y) == (approx(EXAMPLE_PROJECTION[0]), approx(EXAMPLE_PROJECTION[1]))

    proj_x, proj_y = grid_proj.map_geo_to_proj(-3274669.2758, 22150099.56473)
    assert (proj_x, proj_y) == (approx(-110.868173), approx(62.982259))


def test_geo_to_pixel(grid_proj: GridProj):
    pixel_x, pixel_y = grid_proj.map_geo_to_pixel(*EXAMPLE_GEO)
    assert (round(pixel_x, 5), round(pixel_y, 5)) == (0, 0)

    pixel_x, pixel_y = grid_proj.map_geo_to_pixel(-3274669.2758, 22150099.56473)
    assert (pixel_x, pixel_y) == (approx(448.1133948), approx(8824124))


def test_transformations_between_all_formats(grid_proj: GridProj):
    # start with pixel, convert to projection
    initial_pixel = (2000, 1500)
    proj_x, proj_y = grid_proj.map_pixel_to_proj(*initial_pixel)
    initial_proj = (proj_x, proj_y)

    # convert projection to geographic coordinates
    geo_x, geo_y = grid_proj.map_proj_to_geo(proj_x, proj_y)
    initial_geo = geo_x, geo_y

    # convert geographic coordinates back to pixel, full circle, and data should be unchanged
    pixel_x, pixel_y = grid_proj.map_geo_to_pixel(geo_x, geo_y)
    assert (pixel_x, pixel_y) == (approx(initial_pixel[0]), approx(initial_pixel[1]))

    # convert pixel back to geographic coordinates
    geo_x, geo_y = grid_proj.map_pixel_to_geo(pixel_x, pixel_y)
    assert (geo_x, geo_y) == (approx(initial_geo[0]), approx(initial_geo[1]))

    # convert geographic coordinates back to projection
    proj_x, proj_y = grid_proj.map_geo_to_proj(geo_x, geo_y)
    assert (proj_x, proj_y) == (approx(initial_proj[0]), approx(initial_proj[1]))

"""Test suite for vectaster.py"""

# ----------------------------------------------------------------------------------
# Created on Mon Dec 8 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name
# pylint: disable=no-name-in-module,duplicate-code

from unittest.mock import Mock

import numpy
from shapely import equals_exact
from pytest import fixture, MonkeyPatch

from idsse.common.sci.grid_proj import GridProj
from idsse.common.sci.vectaster import (
    geographic_to_pixel,
    geographic_linestring_to_pixel,
    geographic_point_to_pixel,
    geographic_polygon_to_pixel,
    from_wkt,
    rasterize,
    rasterize_point,
    rasterize_linestring,
    rasterize_polygon,
)


EXAMPLE_PROJ_SPEC = "+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +a=6371200"
EXAMPLE_GRID_SPEC = "+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766"


@fixture
def grid_proj() -> GridProj:
    return GridProj.from_proj_grid_spec(EXAMPLE_PROJ_SPEC, EXAMPLE_GRID_SPEC)


# test
def test_geographic_point_to_pixel(grid_proj: GridProj):
    point = from_wkt("POINT (-105 40)")
    pixel_point = from_wkt("POINT (940.528232 781.34269)")
    result = geographic_point_to_pixel(point, grid_proj)

    assert equals_exact(result, pixel_point, tolerance=0.00001)


def test_geographic_linestring_to_pixel(grid_proj: GridProj):
    geo_linestring = from_wkt("LINESTRING (-100 30, -110 40, -120 50)")
    pixel_linestring = from_wkt(
        "LINESTRING (1097.723937 326.578601, 767.38036 797.352492, 509.396013 1309.282566)"
    )
    result = geographic_linestring_to_pixel(geo_linestring, grid_proj)
    assert equals_exact(result, pixel_linestring, tolerance=0.000001)


def test_geographic_polygon_to_pixel(grid_proj: GridProj):
    geo_poly = from_wkt(
        "POLYGON ((-105 40, -110 40, -110 50, -105 50, -105 40), "
        "(-107 42, -107 47, -108 47, -108 42, -107 42))"
    )
    pixel_poly = from_wkt(
        "POLYGON ((940.528232 781.342692,"
        "767.38036 797.352492,"
        "819.139672 1263.254301,"
        "975.073597 1248.836157,"
        "940.528232 781.342692),"
        "(879.268312 877.905408,"
        "899.88468 1110.216016,"
        "867.636632 1113.197772,"
        "845.307299 881.045550,"
        "879.268312 877.905408))"
    )
    result = geographic_polygon_to_pixel(geo_poly, grid_proj)
    assert equals_exact(result, pixel_poly, tolerance=0.000001)


def test_geographic_to_pixel(monkeypatch: MonkeyPatch, grid_proj: GridProj):
    point = from_wkt("POINT (-105 40)")
    line_string = from_wkt("LINESTRING (-105 40, -110 40, -110 50)")
    polygon = from_wkt("POLYGON ((-105 40, -110 40, -110 50, -105 50, -105 40))")

    point_mock = Mock()
    line_str_mock = Mock()
    polygon_mock = Mock()
    monkeypatch.setattr("idsse.common.sci.vectaster.geographic_point_to_pixel", point_mock)
    monkeypatch.setattr("idsse.common.sci.vectaster.geographic_linestring_to_pixel", line_str_mock)
    monkeypatch.setattr("idsse.common.sci.vectaster.geographic_polygon_to_pixel", polygon_mock)

    _ = geographic_to_pixel(point, grid_proj)
    point_mock.assert_called_once_with(point, grid_proj, None)

    _ = geographic_to_pixel(line_string, grid_proj)
    line_str_mock.assert_called_once_with(line_string, grid_proj, None)

    _ = geographic_to_pixel(polygon, grid_proj)
    polygon_mock.assert_called_once_with(polygon, grid_proj, None)


def test_rasterize_point(grid_proj: GridProj):
    point = "POINT (-100.5 30.5)"
    pixels = (numpy.array([1079]), numpy.array([349]))
    result = rasterize_point(point, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_point_from_coord(grid_proj: GridProj):
    point = (-100.5, 30.5)
    pixels = (numpy.array([1079]), numpy.array([349]))
    result = rasterize_point(point, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_point_without_grid_proj():
    point = from_wkt("POINT (1001.5 1130.5)")
    pixels = (numpy.array([1001]), numpy.array([1130]))
    # default round in floor
    result = rasterize_point(point)
    numpy.testing.assert_array_equal(result, pixels)

    pixels = (numpy.array([1002]), numpy.array([1131]))
    # rounding='round' means round half away from zero (both even and odd)
    result = rasterize_point(point, rounding="round")
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_linestring(grid_proj: GridProj):
    linestring = "LINESTRING (-100 30, -100.1 30.1, -100.2 30)"
    pixels = (
        numpy.array([1090, 1091, 1092, 1092, 1093, 1094, 1095, 1095, 1096, 1096, 1097]),
        numpy.array([326, 327, 328, 329, 330, 331, 329, 330, 327, 328, 326]),
    )
    result = rasterize_linestring(linestring, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_polygon_as_linestring(grid_proj: GridProj):
    poly = from_wkt("POLYGON ((0 0, 0 5, 5 5, 5 0, 0 0), (1 1, 3 1, 3 4, 1 4, 1 1))")
    # fmt: off
    pixels = (
        numpy.array(
            [
                0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 2, 2, 3,
                3, 3, 3,
            ]
        ),
        numpy.array(
            [
                0, 1, 2, 3, 4, 5, 0, 5, 0, 5, 0, 5, 0, 5, 0, 1, 2, 3, 4, 5, 1, 2, 3, 4, 1, 4, 1,
                2, 3, 4,
            ]
        ),
    )
    # fmt: on
    result = rasterize_linestring(poly, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_linestring_from_coords(grid_proj: GridProj):
    linestring = [(-100, 30), (-100.01, 30.02), (-100.02, 30)]
    pixels = (numpy.array([1096, 1097, 1097]), numpy.array([326, 326, 327]))
    result = rasterize_linestring(linestring, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_polygon(grid_proj: GridProj):
    poly = "POLYGON ((-105 40, -105.1 40, -105.1 40.1, -105 40.1, -105 40))"
    # fmt: off
    pixels = (
        numpy.array(
            [
                937, 937, 937, 937, 937, 937, 938, 938, 938, 938, 938, 938, 939, 939, 939, 939,
                939, 940, 940, 940, 940, 940,
            ]
        ),
        numpy.array(
            [
                781, 782, 783, 784, 785, 786, 781, 782, 783, 784, 785, 786, 781, 782, 783, 784,
                785, 781, 782, 783, 784, 785,
            ]
        ),
    )
    # fmt: on
    result = rasterize_polygon(poly, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_polygon_from_coords(grid_proj: GridProj):
    poly = (((-105, 40), (-105.1, 40), (-105.1, 40.1), (-105, 40)),)
    pixels = (
        numpy.array([937, 937, 937, 937, 937, 937, 938, 938, 938, 938, 938, 939, 939, 939, 940]),
        numpy.array([781, 782, 783, 784, 785, 786, 781, 782, 783, 784, 785, 781, 782, 783, 781]),
    )
    result = rasterize_polygon(poly, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_polygon_with_hole():
    poly = from_wkt("POLYGON ((0 0, 0 5, 5 5, 5 0, 0 0), (1 1, 3 1, 3 4, 1 4, 1 1))")
    # fmt: off
    pixels = (
        numpy.array(
            [
                0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4,
                4, 5, 5, 5, 5, 5, 5,
            ]
        ),
        numpy.array(
            [
                0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 0, 1, 4, 5, 0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4,
                5, 0, 1, 2, 3, 4, 5,
            ]
        ),
    )
    # fmt: on
    result = rasterize_polygon(poly)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_multi_polygon():
    multi_poly = from_wkt(
        "MULTIPOLYGON (((40 40, 39 41, 41 39, 40 40)), "
        "((20 35, 19 34, 19 33, 22 33, 35 34, 20 35), "
        "(30 20, 28 18, 29 19, 30 20)))"
    )
    # fmt: off
    pixels = (
        numpy.array(
            [
                39, 40, 41, 19, 19, 20, 20, 20, 21, 21, 21, 22, 22, 22, 23, 23, 23, 24, 24, 24,
                25, 25, 25, 26, 26, 26, 27, 27, 27, 28, 28, 29, 30, 31, 32, 33, 34, 35,
            ]
        ),
        numpy.array(
            [
                41, 40, 39, 33, 34, 33, 34, 35, 33, 34, 35, 33, 34, 35, 33, 34, 35, 33, 34, 35,
                33, 34, 35, 33, 34, 35, 33, 34, 35, 33, 34, 34, 34, 34, 34, 34, 34, 34,
            ]
        ),
    )
    # fmt: on
    result = rasterize(multi_poly)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize(monkeypatch: MonkeyPatch, grid_proj: GridProj):
    point = from_wkt("POINT (-105 40)")
    linestring = from_wkt("LINESTRING (-105 40, -110 40, -110 50)")
    polygon = "POLYGON ((-105 40, -110 40, -110 50, -105 50, -105 40))"

    point_mock = Mock()
    linestring_mock = Mock()
    polygon_mock = Mock()
    monkeypatch.setattr("idsse.common.sci.vectaster.rasterize_point", point_mock)
    monkeypatch.setattr("idsse.common.sci.vectaster.rasterize_linestring", linestring_mock)
    monkeypatch.setattr("idsse.common.sci.vectaster.rasterize_polygon", polygon_mock)

    rasterize(point, grid_proj)
    point_mock.assert_called_once()

    rasterize(linestring, grid_proj)
    linestring_mock.assert_called_once()

    rasterize(polygon, grid_proj)
    polygon_mock.assert_called_once()

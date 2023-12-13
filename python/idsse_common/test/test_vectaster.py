'''Test suite for vectaster.py'''
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
from pytest import fixture, MonkeyPatch

from idsse.common.grid_proj import GridProj
from idsse.common.vectaster import (geographic_geometry_to_pixel,
                                    geographic_linestring_to_pixel,
                                    geographic_polygon_to_pixel,
                                    from_wkt,
                                    rasterize,
                                    rasterize_point,
                                    rasterize_linestring,
                                    rasterize_polygon)


EXAMPLE_PROJ_SPEC = '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200'
EXAMPLE_GRID_SPEC = '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766'


@fixture
def grid_proj() -> GridProj:
    return GridProj.from_proj_grid_spec(EXAMPLE_PROJ_SPEC, EXAMPLE_GRID_SPEC)


# test
def test_geographic_linestring_to_pixel(grid_proj: GridProj):
    linestring = from_wkt('LINESTRING (-100 30, -110 40, -120 50)')
    pixel_linestring = from_wkt('LINESTRING (1099.1941683923565 324.546444238068,'
                                '768.0092501944506 794.3170139903758,'
                                '509.1550445412777 1305.9671045297775)')
    result = geographic_linestring_to_pixel(linestring, grid_proj)
    assert result == pixel_linestring


def test_geographic_polygon_to_pixel(grid_proj: GridProj):
    poly = from_wkt('POLYGON ((-105 40, -110 40, -110 50, -105 50, -105 40), '
                    '(-107 42, -107 47, -108 47, -108 42, -107 42))')
    pixel_poly = from_wkt('POLYGON ((941.5576426719887 778.2701810387533,'
                          '768.0092501944506 794.3170139903758,'
                          '819.7238357524881 1259.816223819563,'
                          '976.0731562314586 1245.359671430866,'
                          '941.5576426719887 778.2701810387533),'
                          '(880.1253951755987 874.7112000835223,'
                          '900.7222774204608 1106.8022369109524,'
                          '868.391509125368 1109.7916419444564,'
                          '846.0832806150518 877.8588416022637,'
                          '880.1253951755987 874.7112000835223))')
    result = geographic_polygon_to_pixel(poly, grid_proj)
    assert result == pixel_poly


def test_geographic_to_pixel(monkeypatch: MonkeyPatch, grid_proj: GridProj):
    line_string = from_wkt('LINESTRING (-105 40, -110 40, -110 50)')
    polygon = from_wkt('POLYGON ((-105 40, -110 40, -110 50, -105 50, -105 40))')

    line_string_mock = Mock()
    polygon_mock = Mock()
    monkeypatch.setattr('idsse.common.vectaster.geographic_linestring_to_pixel', line_string_mock)
    monkeypatch.setattr('idsse.common.vectaster.geographic_polygon_to_pixel', polygon_mock)

    geographic_geometry_to_pixel(line_string, grid_proj)
    line_string_mock.assert_called_once()
    geographic_geometry_to_pixel(polygon, grid_proj)
    polygon_mock.assert_called_once()


def test_rasterize_point(grid_proj: GridProj):
    linestring = from_wkt('POINT (-100.5 30.5)')
    pixels = ((numpy.array([1081]), numpy.array([347])))
    result = rasterize_point(linestring, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_linestring(grid_proj: GridProj):
    linestring = from_wkt('LINESTRING (-100 30, -100.1 30.1, -100.2 30)')
    pixels = (numpy.array([1099, 1098, 1097, 1097, 1096, 1095, 1094, 1093, 1093, 1092, 1091]),
              numpy.array([324, 325, 326, 327, 328, 329, 328, 327, 326, 325, 324]))
    result = rasterize_linestring(linestring, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_polygon(grid_proj: GridProj):
    poly = from_wkt('POLYGON ((-105 40, -105.1 40, -105.1 40.1, -105 40.1, -105 40))')
    pixels = (numpy.array([938, 939, 940, 941, 938, 939, 940, 941, 938, 939, 940,
                           941, 938, 939, 940, 941, 938, 939, 940, 941, 941, 938]),
              numpy.array([778, 778, 778, 778, 779, 779, 779, 779, 780, 780, 780,
                           780, 781, 781, 781, 781, 782, 782, 782, 782, 782, 783]))
    result = rasterize_polygon(poly, grid_proj)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize_polygon_with_hole():
    poly = from_wkt('POLYGON ((0 0, 0 5, 5 5, 5 0, 0 0), (1 1, 3 1, 3 4, 1 4, 1 1))')
    pixels = (numpy.array([0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5, 0, 1, 3, 4, 5,
                           0, 1, 3, 4, 5, 0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]),
              numpy.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2,
                           3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5]))
    result = rasterize_polygon(poly)
    numpy.testing.assert_array_equal(result, pixels)


def test_rasterize(monkeypatch: MonkeyPatch, grid_proj: GridProj):
    point = from_wkt('POINT (-105 40)')
    linestring = from_wkt('LINESTRING (-105 40, -110 40, -110 50)')
    polygon = from_wkt('POLYGON ((-105 40, -110 40, -110 50, -105 50, -105 40))')

    point_mock = Mock()
    linestring_mock = Mock()
    polygon_mock = Mock()
    monkeypatch.setattr('idsse.common.vectaster.rasterize_point', point_mock)
    monkeypatch.setattr('idsse.common.vectaster.rasterize_linestring', linestring_mock)
    monkeypatch.setattr('idsse.common.vectaster.rasterize_polygon', polygon_mock)

    rasterize(point, grid_proj)
    point_mock.assert_called_once()
    rasterize(linestring, grid_proj)

    linestring_mock.assert_called_once()
    rasterize(polygon, grid_proj)
    polygon_mock.assert_called_once()

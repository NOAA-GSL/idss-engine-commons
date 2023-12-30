"""Test suite for image_utils.py"""
# ----------------------------------------------------------------------------------
# Created on Fri Dec 29 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring
import numpy

from pytest import fixture

from idsse.common.grid_proj import GridProj
from idsse.common.image_utils import GeoImage


@fixture
def proj_spec():
    return '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200'


@fixture
def grid_spec():
    return '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766'


def test_geo_image_from_data_grid(proj_spec, grid_spec):
    proj = GridProj.from_proj_grid_spec(proj_spec, grid_spec)
    print(proj)
    data = numpy.array([[0, 1, 2, 3],
                        [4, 5, 6, 7],
                        [8, 9, 10, 11]])
    scale = 30
    width, height = 10, 5
    data = numpy.array([x*1.3+30 for x in range(width*height)]).reshape(height, width)
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    geo_image.outline_pixel(2, 2, (255, 0, 0))
    geo_image.set_pixel(2, 4, (0, 255, 0))
    ij1 = (2.1, 2.1)
    ij2 = (2.9, 4.9)
    geo_image.draw_point(*ij1, (0, 0, 255))
    geo_image.draw_point(*ij2, (0, 0, 255))
    # print("before draw line")
    geo_image.draw_line_seg(*ij1, *ij2, (0, 0, 255))
    geo_image.draw_shape('POLYGON((1.1 1.1, 1.5 1.9, 1.9 1.1, 1.1 1.1))', (0, 0, 255))
    line_string = 'LINESTRING(1.5 7.5, 3.25 8.75)'
    geo_image.set_pixel_for_shape(line_string, (0, 255, 255))
    geo_image.draw_shape(line_string, (255, 0, 255))
    geo_image.outline_pixel_for_shape(line_string, (255, 0, 0))
    geo_image.show()
    assert False


if __name__ == '__main__':
    test_geo_image_from_data_grid(
        '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200',
        '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766'
    )

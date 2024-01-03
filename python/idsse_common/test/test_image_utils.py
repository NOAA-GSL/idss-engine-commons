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
# pylint: disable=missing-function-docstring, redefined-outer-name
import numpy

from pytest import fixture

from idsse.common.grid_proj import GridProj
from idsse.common.image_utils import GeoImage


@fixture
def proj():
    proj_spec = '+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +r=6371200'
    grid_spec = '+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766'
    return GridProj.from_proj_grid_spec(proj_spec, grid_spec)


def test_geo_image_from_data_grid(proj):
    data = numpy.array([[0, 1, 2, 3],
                        [4, 5, 6, 7],
                        [8, 9, 10, 11]])

    geo_image = GeoImage.from_data_grid(proj, data)
    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    # every value comes in groups of three since the colors are on a grey scale (one each for rgb)
    expected_values = [0, 23, 46, 69, 92, 115, 139, 162, 185, 208, 231, 255]
    expected_indices = numpy.repeat(data, 3)
    numpy.testing.assert_array_equal(values, expected_values)
    numpy.testing.assert_array_equal(indices, expected_indices)
    assert all(cnt == 3 for cnt in counts)


def test_geo_image_from_data_grid_with_scale(proj):
    data = numpy.array([[0, 1, 2, 3],
                        [4, 5, 6, 7],
                        [8, 9, 10, 11]])

    scale = 5
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    expected_values = [0, 23, 46, 69, 92, 115, 139, 162, 185, 208, 231, 255]
    expected_indices = numpy.repeat(numpy.repeat(data, [scale, scale, scale], axis=0), scale * 3)
    numpy.testing.assert_array_equal(values, expected_values)
    numpy.testing.assert_array_equal(indices, expected_indices)
    assert all(cnt == scale * scale * 3 for cnt in counts)


def test_set_pixel(proj):
    scale = 5
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j = (1.9, 4.9)
    geo_image.set_pixel(*i_j, (100, 100, 100))

    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)
    # values will be 100 (for set pixel) and 255 everywhere else
    numpy.testing.assert_array_equal(values, [100, 255])
    numpy.testing.assert_array_equal(counts, [75, 3675])
    expected_indices = [810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820,
                        821, 822, 823, 824, 960, 961, 962, 963, 964, 965, 966,
                        967, 968, 969, 970, 971, 972, 973, 974, 1110, 1111, 1112,
                        1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123,
                        1124, 1260, 1261, 1262, 1263, 1264, 1265, 1266, 1267, 1268, 1269,
                        1270, 1271, 1272, 1273, 1274, 1410, 1411, 1412, 1413, 1414, 1415,
                        1416, 1417, 1418, 1419, 1420, 1421, 1422, 1423, 1424]
    numpy.testing.assert_array_equal(numpy.where(indices == 0)[0], expected_indices)


def test_outline_pixel(proj):
    scale = 5
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j = (1.1, 2.1)
    geo_image.outline_pixel(*i_j, (100, 100, 100))

    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    # values will be 100 (for outlined pixel) and 255 everywhere else
    numpy.testing.assert_array_equal(values, [100, 255])
    numpy.testing.assert_array_equal(counts, [48, 3702])
    expected_indices = [780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790,
                        791, 792, 793, 794, 930, 931, 932, 942, 943, 944, 1080,
                        1081, 1082, 1092, 1093, 1094, 1230, 1231, 1232, 1242, 1243, 1244,
                        1380, 1381, 1382, 1383, 1384, 1385, 1386, 1387, 1388, 1389, 1390,
                        1391, 1392, 1393, 1394]
    numpy.testing.assert_array_equal(numpy.where(indices == 0)[0], expected_indices)


def test_draw_point(proj):
    scale = 10
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j = (1.1, 2.1)
    geo_image.draw_point(*i_j, (100, 0, 0))

    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    # values will be 0 and 100 (for single point) and 255 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100, 255])
    numpy.testing.assert_array_equal(counts, [2, 1, 14997])
    expected_indices = [3363]
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)


def test_draw_line_seg(proj):
    scale = 50
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j_1 = (1.1, 2.1)
    i_j_2 = (1.9, 4.9)

    geo_image.draw_line_seg(*i_j_1, *i_j_2, (100, 0, 0))

    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    # values will be 0 or 100 (for line seg) and 255 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100, 255])
    numpy.testing.assert_array_equal(counts, [282, 141, 374577])
    expected_indices = [82815, 82818, 84321, 84324, 84327, 84330, 85833, 85836,
                        85839, 87342, 87345, 87348, 87351, 88854, 88857, 88860,
                        90363, 90366, 90369, 90372, 91875, 91878, 91881, 93384,
                        93387, 93390, 93393, 94896, 94899, 94902, 96405, 96408,
                        96411, 96414, 97917, 97920, 97923, 99426, 99429, 99432,
                        99435, 100938, 100941, 100944, 102447, 102450, 102453, 102456,
                        103959, 103962, 103965, 105468, 105471, 105474, 105477, 106980,
                        106983, 106986, 108489, 108492, 108495, 108498, 110001, 110004,
                        110007, 111510, 111513, 111516, 111519, 113022, 113025, 113028,
                        114531, 114534, 114537, 114540, 116043, 116046, 116049, 117552,
                        117555, 117558, 117561, 119064, 119067, 119070, 120573, 120576,
                        120579, 120582, 122085, 122088, 122091, 123594, 123597, 123600,
                        123603, 125106, 125109, 125112, 126615, 126618, 126621, 126624,
                        128127, 128130, 128133, 129636, 129639, 129642, 129645, 131148,
                        131151, 131154, 132657, 132660, 132663, 132666, 134169, 134172,
                        134175, 135678, 135681, 135684, 135687, 137190, 137193, 137196,
                        138699, 138702, 138705, 138708, 140211, 140214, 140217, 141720,
                        141723, 141726, 141729, 143232, 143235]
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)


def test_draw_polygon(proj):
    scale = 3
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)

    geo_image.draw_shape('POLYGON((1.1 1.1, 1.5 1.9, 1.9 1.1, 1.1 1.1))', (0, 100, 100))

    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    # values will be 0 or 100 (for polygon) and 255 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100, 255])
    numpy.testing.assert_array_equal(counts, [6, 12, 1332])
    expected_indices = [279, 282, 369, 372, 375, 459]
    numpy.testing.assert_array_equal(numpy.where(indices == 0)[0], expected_indices)


def test_set_outline_pixel_for_shape(proj):
    scale = 3
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)

    geo_image.set_pixel_for_shape('LINESTRING(1.5 7.5, 3.25 8.75)', (0, 100, 100))
    geo_image.outline_pixel_for_shape('POINT(2.3 4)', (1, 100, 100))

    values, indices, counts = numpy.unique(geo_image.rgb_array,
                                           return_inverse=True,
                                           return_counts=True)

    numpy.testing.assert_array_equal(values, [0, 1, 100, 255])
    numpy.testing.assert_array_equal(counts, [27, 8, 70, 1245])
    expected_indices = [333, 336, 339, 423, 426, 429, 513, 516, 519, 612, 615,
                        618, 702, 705, 708, 792, 795, 798, 882, 885, 888, 972,
                        975, 978, 1062, 1065, 1068]
    numpy.testing.assert_array_equal(numpy.where(indices == 0)[0], expected_indices)
    expected_indices = [576, 579, 582, 666, 672, 756, 759, 762]
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)

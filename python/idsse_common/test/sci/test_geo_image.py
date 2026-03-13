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
import os

import numpy
from pytest import fixture, approx

from idsse.common.sci.geo_image import ColorPalette, GeoImage, normalize, scale_to_color_palette
from idsse.common.sci.grid_proj import GridProj
from idsse.common.sci.netcdf_io import read_netcdf


@fixture
def proj():
    proj_spec = "+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +a=6371200"
    grid_spec = "+dx=2539.703 +dy=2539.703 +w=2345 +h=1597 +lat_ll=19.229 +lon_ll=-126.2766"
    return GridProj.from_proj_grid_spec(proj_spec, grid_spec)


def test_geo_image_without_data_grid(proj):
    fill_color = (255, 0, 0)
    geo_image = GeoImage.from_proj(proj, fill_color)
    values, _, counts = numpy.unique(geo_image.rgb_array, return_inverse=True, return_counts=True)
    # the only value in the grid should be 0 and 255, where there should be twice as many
    # 0 as 255 and the total count should be 11234895 (proj width*height)
    numpy.testing.assert_array_equal(values, [0, 255])
    numpy.testing.assert_array_equal(counts, [7489930, 3744965])
    assert sum(counts) == 11234895


def test_geo_image_from_data_grid(proj):
    data = numpy.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]])

    geo_image = GeoImage.from_data_grid(proj, data)
    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    # every value comes in groups of three since the colors are on a grey scale (one each for rgb)
    expected_values = [0, 23, 46, 69, 92, 115, 139, 162, 185, 208, 231, 255]
    expected_indices = numpy.repeat(data, 3)
    numpy.testing.assert_array_equal(values, expected_values)
    numpy.testing.assert_array_equal(indices.flatten(), expected_indices)
    assert all(cnt == 3 for cnt in counts)


def test_geo_image_from_data_grid_with_scale(proj):
    data = numpy.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]])

    scale = 5
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    expected_values = [0, 23, 46, 69, 92, 115, 139, 162, 185, 208, 231, 255]
    expected_indices = numpy.repeat(numpy.repeat(data, [scale, scale, scale], axis=0), scale * 3)
    numpy.testing.assert_array_equal(values, expected_values)
    numpy.testing.assert_array_equal(indices.flatten(), expected_indices)
    assert all(cnt == scale * scale * 3 for cnt in counts)


def test_set_pixel(proj):
    scale = 5
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j = (1.9, 4.9)
    geo_image.set_pixel(*i_j, (100, 100, 100), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )
    # values will be 100 (for set pixel) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    numpy.testing.assert_array_equal(counts, [3675, 75])
    # fmt: off
    expected_indices = [
        5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6,
        6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
        7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9,
        9, 9, 9, 9, 9, 9, 9, 9, 9
    ]
    # fmt: on
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)


def test_outline_pixel(proj):
    scale = 5
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j = (1.1, 2.1)
    geo_image.outline_pixel(*i_j, (100, 100, 100), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    # values will be 100 (for outlined pixel) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    numpy.testing.assert_array_equal(counts, [3702, 48])
    # fmt: off
    expected_indices = [
        5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 7,
        7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9,
        9, 9, 9, 9
    ]
    # fmt: on
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)


def test_draw_point(proj):
    scale = 10
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j = (1.1, 2.1)
    geo_image.draw_point(*i_j, (100, 0, 0), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    # values will be 0 and 100 (for single point) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    numpy.testing.assert_array_equal(counts, [14999, 1])
    expected_indices = [11]
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)


def test_draw_line_seg(proj):
    scale = 50
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)
    i_j_1 = (1.1, 2.1)
    i_j_2 = (1.9, 4.9)

    geo_image.draw_line_seg(*i_j_1, *i_j_2, (100, 0, 0), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    # values will be 0 or 100 (for line seg) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    numpy.testing.assert_array_equal(counts, [374859, 141])
    # fmt: off
    expected_indices = [
        55, 55, 56, 56, 56, 56, 57, 57, 57, 58, 58, 58, 58, 59, 59, 59, 60,
        60, 60, 60, 61, 61, 61, 62, 62, 62, 62, 63, 63, 63, 64, 64, 64, 64,
        65, 65, 65, 66, 66, 66, 66, 67, 67, 67, 68, 68, 68, 68, 69, 69, 69,
        70, 70, 70, 70, 71, 71, 71, 72, 72, 72, 72, 73, 73, 73, 74, 74, 74,
        74, 75, 75, 75, 76, 76, 76, 76, 77, 77, 77, 78, 78, 78, 78, 79, 79,
        79, 80, 80, 80, 80, 81, 81, 81, 82, 82, 82, 82, 83, 83, 83, 84, 84,
        84, 84, 85, 85, 85, 86, 86, 86, 86, 87, 87, 87, 88, 88, 88, 88, 89,
        89, 89, 90, 90, 90, 90, 91, 91, 91, 92, 92, 92, 92, 93, 93, 93, 94,
        94, 94, 94, 95, 95
    ]
    # fmt: on
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0], expected_indices)


def test_draw_polygon(proj):
    scale = 3
    width, height = 3, 3
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)

    geo_image.draw_shape("POLYGON((1.1 1.1, 1.5 1.9, 1.9 1.1, 1.1 1.1))", (0, 100, 0), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    # values will be 0 or 100 (for polygon) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    numpy.testing.assert_array_equal(counts, [237, 6])
    expected_indices = [3, 3, 4, 4, 4, 5]
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0].flatten(), expected_indices)


def test_draw_multi_polygon(proj):
    scale = 3
    width, height = 4, 4
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)

    multi_poly = (
        "MULTIPOLYGON (((1.1 1.1, 1.1 1.9, 1.9 1.9, 1.9 1.1, 1.1 1.1)),"
        "((2.1 2.1, 2.5 2.9, 2.9 2.1, 2.1 2.1)))"
    )
    geo_image.draw_shape(multi_poly, (0, 100, 0), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    # values will be 0 or 100 (for polygon) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    numpy.testing.assert_array_equal(counts, [416, 16])
    expected_indices = [3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 7, 8, 8]
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0].flatten(), expected_indices)


def test_draw_geo_polygon(proj: GridProj):
    scale = 10
    width, height = 5, 5
    lon_lat_1 = proj.map_pixel_to_geo(1.5, 1.0)
    lon_lat_2 = proj.map_pixel_to_geo(3.5, 1.0)
    lon_lat_3 = proj.map_pixel_to_geo(1.5, 3.5)
    poly_wkt = (
        f"POLYGON(({lon_lat_1[0]} {lon_lat_1[1]}, {lon_lat_2[0]} {lon_lat_2[1]}, "
        f"{lon_lat_3[0]} {lon_lat_3[1]}, {lon_lat_1[0]} {lon_lat_1[1]}))"
    )
    geo_image = GeoImage.from_data_grid(proj, numpy.zeros((height, width)), scale=scale)

    geo_image.draw_shape(poly_wkt, (0, 0, 100))

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )
    # values will be 0 or 100 (for polygon) and 0 everywhere else
    numpy.testing.assert_array_equal(values, [0, 100])
    # the "equality" workarounds below are needed due to counts and indices arrays having
    # different results when run with pytest locally vs. in GitHub Actions runner (OS-dependent)
    assert counts.tolist() == approx([7190, 310], rel=0.20)  # counts can be up to 20% off
    # fmt: off
    expected_indices = [
        14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35
    ]
    # fmt: on
    # require at least 90% of the expected colored pixels to have been actually colored
    actual_indices = numpy.where(indices == 1)[0].flatten()
    indices_in_both = set(expected_indices).intersection(set(actual_indices))
    assert (len(indices_in_both) / len(expected_indices)) >= 0.90


def test_set_outline_pixel_for_shape(proj):
    scale = 3
    width, height = 10, 5
    data = numpy.zeros((height, width))
    geo_image = GeoImage.from_data_grid(proj, data, scale=scale)

    geo_image.set_pixel_for_shape("LINESTRING(1.5 7.5, 3.25 8.75)", (1, 100, 100), geo=False)
    geo_image.outline_pixel_for_shape("POINT(2.3 4)", (2, 100, 100), geo=False)

    values, indices, counts = numpy.unique(
        geo_image.rgb_array, return_inverse=True, return_counts=True
    )

    numpy.testing.assert_array_equal(values, [0, 1, 2, 100])

    numpy.testing.assert_array_equal(counts, [1245, 27, 8, 70])
    # fmt: off
    expected_indices = [
        3,  3,  3,  4,  4,  4,  5,  5,  5,  6,  6,  6,  7,  7,  7,  8,  8,
        8,  9,  9,  9, 10, 10, 10, 11, 11, 11
    ]
    # fmt: on
    numpy.testing.assert_array_equal(numpy.where(indices == 1)[0].flatten(), expected_indices)
    expected_indices = [6, 6, 6, 7, 7, 8, 8, 8]
    numpy.testing.assert_array_equal(numpy.where(indices == 2)[0].flatten(), expected_indices)


def test_normalize():
    data_array = numpy.array([[0, 1, 2], [3, 4, 5]])
    norm_array = normalize(data_array)

    numpy.testing.assert_allclose(norm_array, [[0.0, 0.2, 0.4], [0.6, 0.8, 1.0]], atol=0.00001)


def test_normalize_with_excludes():
    data_array = numpy.array([[0, 1, 2], [3, 4, 5]])
    norm_array = normalize(data_array, min_value=1, max_value=4, missing_value=3)

    numpy.testing.assert_allclose(
        norm_array, [[-1.0, 0.0, 0.3333333], [numpy.nan, 1.0, 2.0]], atol=0.00001
    )
    numpy.testing.assert_array_equal(norm_array.mask, [[True, False, False], [True, False, True]])


def test_scale_to_color_palette():
    norm_array = numpy.array([[0.0, 0.2, 0.4], [0.6, 0.8, 1.0]])
    index_array = scale_to_color_palette(norm_array, 256)

    numpy.testing.assert_array_equal(index_array, [[0, 51, 102], [153, 204, 255]])


def test_scale_to_color_palette_force_excludes():
    norm_array = numpy.array([[-1.0, 0.0, 0.3333333], [numpy.nan, 1.0, 2.0]])
    index_array = scale_to_color_palette(norm_array, 256)

    numpy.testing.assert_array_equal(index_array, [[0, 0, 84], [0, 255, 255]])


def test_scale_to_color_palette_with_excludes():
    norm_array = numpy.array([[-1.0, 0.0, 0.3333333], [numpy.nan, 1.0, 2.0]])
    index_array = scale_to_color_palette(norm_array, 256, True, True, True)

    numpy.testing.assert_array_equal(index_array, [[256, 0, 84], [258, 255, 257]])


def test_draw_state(proj):
    data = numpy.zeros((proj.width, proj.height))
    geo_image = GeoImage.from_data_grid(proj, data)
    geo_image.draw_state("Rhode Island", color=(255, 0, 0))

    values, counts = numpy.unique(geo_image.rgb_array, return_counts=True)
    numpy.testing.assert_array_equal(values, [0, 255])
    numpy.testing.assert_array_equal(counts, [11234295, 600])


def test_add_one_state(proj):
    data = numpy.zeros((proj.width, proj.height))
    geo_image = GeoImage.from_data_grid(proj, data)
    geo_image.draw_state_boundary("Florida", color=(255, 0, 0))

    # confirm that at least three of the pixel along the state boundary are colored red
    numpy.testing.assert_array_equal(geo_image.rgb_array[1665, 320], [255, 0, 0])
    numpy.testing.assert_array_equal(geo_image.rgb_array[1850, 125], [255, 0, 0])
    numpy.testing.assert_array_equal(geo_image.rgb_array[1812, 109], [255, 0, 0])


def test_add_list_of_states(proj):
    data = numpy.zeros((proj.width, proj.height))
    geo_image = GeoImage.from_data_grid(proj, data)
    geo_image.draw_state_boundary(["Nevada", "Iowa", "Delaware"], color=(255, 0, 0))

    # confirm that at least three of the pixel along state boundaries are colored red
    numpy.testing.assert_array_equal(geo_image.rgb_array[608, 682], [255, 0, 0])
    numpy.testing.assert_array_equal(geo_image.rgb_array[1263, 795], [255, 0, 0])
    numpy.testing.assert_array_equal(geo_image.rgb_array[1956, 797], [255, 0, 0])


def test_color_palette():
    # get grey scale color palette (with excludes given default arg)
    color_palette = ColorPalette.grey()
    # length of the lookup table should be 256 (0->255) plus 3 extra for the excludes
    assert len(color_palette.lut) == 256 + 3
    # check that each rgb value matches it's position
    for idx, (red, green, blue) in enumerate(color_palette.lut[:256]):
        assert idx == red == green == blue


def test_color_palette_with_anchor():
    color_palette = ColorPalette.linear(
        [(0, 0, 0), (100, 100, 100), (255, 255, 255)], [0, 100, 255]
    )
    # this color palette will not have exclude
    assert len(color_palette.lut) == 256
    # without the anchors the value would not match position
    for idx, (red, green, blue) in enumerate(color_palette.lut[:256]):
        assert idx == red == green == blue


def test_add_all_states(proj):
    filename = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..",
        "resources",
        "nbm_temp-202211111100-202211121300.nc",
    )

    attrs, data = read_netcdf(filename, use_h5_lib=True)
    if attrs["data_order"] == "latitude,longitude":
        data = numpy.transpose(data)
    geo_image = GeoImage.from_data_grid(proj, data)
    geo_image.draw_state_boundary("All", color=(255, 0, 0))

    # confirm that at least three of the pixel along state boundaries are colored red
    numpy.testing.assert_array_equal(geo_image.rgb_array[1707, 861], [255, 0, 0])
    numpy.testing.assert_array_equal(geo_image.rgb_array[742, 889], [255, 0, 0])
    numpy.testing.assert_array_equal(geo_image.rgb_array[1206, 229], [255, 0, 0])

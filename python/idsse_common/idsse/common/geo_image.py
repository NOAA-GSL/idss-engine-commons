"""Utility for generating geo referenced images"""
# ----------------------------------------------------------------------------------
# Created on Fri Dec 29 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
import functools
import json
import logging
import math
import os
from typing import NamedTuple, Self

import numpy as np
from PIL import Image
from shapely import from_geojson, from_wkt, Geometry, LineString, MultiPolygon, Polygon


from .grid_proj import GridProj
from .vectaster import geographic_to_pixel, rasterize

logger = logging.getLogger(__name__)


class Color(NamedTuple):
    """Data class used to hold RGB colors"""
    red: float
    green: float
    blue: float


ColorPalette = np.ndarray[Color]


class GeoImage():
    """AWS Utility Class"""

    def __init__(self, proj: GridProj, rgb_array: np.ndarray, scale: int = 1):
        self.proj = proj
        self.rgb_array = rgb_array
        self.scale = scale

    @classmethod
    def from_index_grid(
        cls,
        proj: GridProj,
        index_array: np.ndarray,
        colors: ColorPalette | None = None,
        scale: int = 1
    ) -> Self:
        """Method for building a geographical image from backing data in a ndarray

        Args:
            proj (GridProj): Grid projection to be used for this geo image, must match data_grid
            data_grid (np.ndarray): Data to be used as base layer, such as a temperature field
            colors (ColorPalette | None): The color palette used to map the data grid to color.
                                          Defaults to None, in which case a grey scale will be used.
            scale (int, optional): The height and width that a grid cell will be scaled to in the
                                   image. Defaults to 1.

        Returns:
            Self: GeoImage
        """
        if colors is None:
            lut = np.array(_get_grey_scale(), dtype=np.uint8)
        else:
            lut = np.array(colors, dtype=np.uint8)

        if scale != 1:
            index_array = np.repeat(np.repeat(index_array, scale, axis=1), scale, axis=0)
        rgb_array = lut[index_array]

        return GeoImage(proj, rgb_array, scale)

    @classmethod
    def from_data_grid(
        cls,
        proj: GridProj,
        data_array: np.ndarray,
        colors: ColorPalette | None = None,
        scale: int = 1
    ) -> Self:
        """Method for building a geographical image from backing data in a ndarray

        Args:
            proj (GridProj): Grid projection to be used for this geo image, must match data_grid
            data_grid (np.ndarray): Data to be used as base layer, such as a temperature field
            colors (ColorPalette | None): The color palette used to map the data grid to color.
                                          Defaults to None, in which case a grey scale will be used.
            scale (int, optional): The height and width that a grid cell will be scaled to in the
                                   image. Defaults to 1.

        Returns:
            Self: GeoImage
        """
        num_colors = 256
        if colors is not None and len(colors) < num_colors:
            num_colors = len(colors)

        index_array = scale_to_color_palette(normalize(data_array), num_colors)
        return GeoImage.from_index_grid(proj, index_array, colors, scale)

    @functools.cached_property
    def shape(self):
        return self.rgb_array.shape

    @functools.cached_property
    def width(self):
        return self.rgb_array.shape[0]

    @functools.cached_property
    def height(self):
        return self.rgb_array.shape[1]

    def show(self):
        """A convenience method for showing the current state of the image"""
        image = Image.fromarray(np.flipud(np.transpose(self.rgb_array, [1, 0, 2])), mode='RGB')
        # image = Image.fromarray(self.rgb_array, mode='RGB')
        image.show()

    def draw_point(self, i: float, j: float, color: Color, geo: bool = True):
        """Draw a point onto the image, will only be one image cell and doesn't make use of scale.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if geo:
            i, j = self.proj.map_geo_to_pixel(i, j)
        self.rgb_array[int(i*self.scale), int(j*self.scale)] = color

    def draw_line_seg(  # pylint: disable=too-many-arguments
            self,
            i_1: float, j_1: float,
            i_2: float, j_2: float,
            color: Color,
            geo: bool = True
            ):
        """Draw a line segment onto the image, will only be on image cell wide
        and doesn't make use of scale.

        Args:
            i_1 (float): Location of the first point, corresponding to the first dim
            j_1 (float): Location of the first point, corresponding to the second dim
            i_2 (float): Location of the second point, corresponding to the first dim
            j_2 (float): Location of the second point, corresponding to the first dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        self.draw_shape(f'LINESTRING ({i_1} {j_1}, {i_2} {j_2})', color, geo=geo)

    def draw_linestring(
        self,
        shape: Geometry,
        color: Color,
        geo: bool = True
    ):
        """Draw the outline of a shape onto the image, treats all parts (exterior, holes, ect)
        as linestrings.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255
            geo (bool): Indication that the shape is specified by geographic coordinates (lon/lat)

        Raises:
            TypeError: Raised when the passed shape in not of a supported type
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        if geo:
            shape = geographic_to_pixel(shape, self.proj)

        if isinstance(shape, LineString):
            self.draw_shape(shape, color, geo=False)
        elif isinstance(shape, Polygon):
            self.draw_shape(shape.exterior, color, geo=False)
            for interior in shape.interiors:
                self.draw_shape(interior, color, geo=False)
        elif isinstance(shape, MultiPolygon):
            for poly in shape.geoms:
                self.draw_linestring(poly, color, geo=False)
        else:
            raise TypeError(f'Passed shape (with type: {type(shape)}) in not currently supported')

    def draw_shape(
        self,
        shape: Geometry,
        color: Color,
        geo: bool = True
    ):
        """Draw a shape onto the image, points and lines will only be on image cell wide
        and polygon will be filled, doesn't make use of scale.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255
            geo (bool): Indication that the shape is specified by geographic coordinates (lon/lat)

        Raises:
            TypeError: Raised when the passed shape in not of a supported type
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        if geo:
            shape = geographic_to_pixel(shape, self.proj)

        if isinstance(shape, LineString):
            vertices = [(int(i*self.scale), int(j*self.scale)) for i, j in shape.coords]
            shape = LineString(vertices)
        elif isinstance(shape, Polygon):
            outer = [(int(i*self.scale), int(j*self.scale)) for i, j in shape.exterior.coords]
            inner = [[(int(i*self.scale), int(j*self.scale)) for i, j in inner.coords]
                     for inner in shape.interiors]
            shape = Polygon(outer, inner)
        elif isinstance(shape, MultiPolygon):
            for poly in shape.geoms:
                self.draw_shape(poly, color, False)
        else:
            raise TypeError(f'Passed shape (with type: {type(shape)}) in not currently supported')

        coords = rasterize(shape)

        for i, j in zip(*coords):
            # print('\t', i_j)
            if 0 <= i < self.width and 0 <= j < self.height:
                self.rgb_array[i, j] = color

    def set_pixel(self, i: float, j: float, color: Color, geo: bool = True):
        """Set all image cell associated with location specified by i, j to the passed color.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if geo:
            i, j = self.proj.map_geo_to_pixel(i, j)

        i = math.floor(i)*self.scale
        j = math.floor(j)*self.scale
        self.rgb_array[i:i+self.scale, j:j+self.scale] = color

    def set_pixel_for_shape(self, shape: Geometry, color: Color, geo: bool = True):
        """Set all image cell associated with geometry to the specified color.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        coords = rasterize(shape, self.proj) if geo else rasterize(shape)
        for i_j in zip(*coords):
            self.set_pixel(*i_j, color, geo=False)

    def outline_pixel(self, i: float, j: float, color: Color, geo: bool = True):
        """Set the image cell associated with outside edge of location specified by i, j
        to the passed color.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if geo:
            i, j = self.proj.map_geo_to_pixel(i, j)

        i = math.floor(i)*self.scale
        j = math.floor(j)*self.scale
        self.rgb_array[i:i+self.scale, j] = color
        self.rgb_array[i:i+self.scale, j+self.scale-1] = color
        self.rgb_array[i, j:j+self.scale] = color
        self.rgb_array[i+self.scale-1, j:j+self.scale] = color

    def outline_pixel_for_shape(self, shape, color, geo: bool = True):
        """Set all image cell associated outside edge of pixels associated with geometry
          to the specified color.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        coords = rasterize(shape, self.proj) if geo else rasterize(shape)
        for i_j in zip(*coords):
            self.outline_pixel(*i_j, color, geo=False)

    def draw_state(self, state: str, color: Color):
        states = _get_states_json()
        self.draw_shape(states[state], color)

    def draw_state_boundary(self, state: str, color: Color):
        states = _get_states_json()
        if state == 'All':
            for name in states:
                self.draw_linestring(states[name], color)
        elif isinstance(state, str):
            self.draw_linestring(states[state], color)
        else:
            for name in state:
                self.draw_linestring(states[name], color)


def normalize(array, min_value=None, max_value=None, missing_value=None, N=None):
    mask = array.mask if np.ma.is_masked(array) else np.isnan(array)

    min_mask = max_mask = missing_mask = None
    if missing_value is not None:
        mask = np.logical_or(mask, array == missing_value, out=mask)
        missing_mask = np.array(mask, copy=True)

    masked_array = np.ma.masked_array(array, mask)

    if min_value is not None:
        min_mask = (masked_array < min_value).data
        min_mask = np.logical_xor(min_mask, np.logical_and(mask, min_mask))
        mask = np.logical_or(mask, min_mask, out=mask)
    if max_value is not None:
        max_mask = (masked_array > max_value).data
        max_mask = np.logical_xor(max_mask, np.logical_and(mask, max_mask))
        mask = np.logical_or(mask, max_mask, out=mask)

    masked_array = np.ma.masked_array(array, mask)

    if min_value is None:
        min_value = np.ma.min(masked_array)

    if max_value is None:
        max_value = np.ma.max(masked_array)

    value_range = max_value - min_value

    array = np.array(array, dtype=np.float32, copy=True)

    array -= min_value
    if value_range:
        array /= value_range

    if min_mask is not None:
        array[min_mask] = -1

    if max_mask is not None:
        array[max_mask] = 2

    if missing_mask is not None:
        array[missing_mask] = np.nan

    if mask is not None and np.any(mask):
        return np.ma.masked_array(array, mask)

    return array


def scale_to_color_palette(norm_array, num_colors,
                           with_under=False, with_over=False, with_fill=False):

    under_idx = num_colors if with_under else 0
    over_idx = num_colors + 1 if with_over else num_colors-1
    bad_idx = num_colors + 2 if with_fill else 0

    with np.errstate(invalid="ignore"):
        array = (norm_array * (num_colors-1)).astype(int)

    if np.ma.is_masked(array):
        norm_array = norm_array.data

    array[norm_array == -1] = under_idx
    array[norm_array == 2] = over_idx
    array[np.isnan(norm_array)] = bad_idx

    return array


def _get_states_json():
    current_path = os.path.dirname(os.path.realpath(__file__))
    states_filename = os.path.join(current_path, 'resources', 'us_states.json')
    with open(states_filename, 'r', encoding='utf8') as file:
        states_json = json.load(file)
    states = {}
    for feature in states_json['features']:
        states[feature['properties']['NAME']] = from_geojson(json.dumps(feature))
    return states


@functools.cache
def _get_grey_scale():
    grey_cm = [(x, x, x) for x in range(0, 256)]
    # tack on three colors (light salmon) to use for under/over/fill values, just in case
    grey_cm.extend((255, 142, 142) for _ in range(3))
    return grey_cm

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
from collections.abc import Sequence
from typing import Any, NamedTuple, Self

import numpy as np
from PIL import Image
from shapely import from_geojson, from_wkt, Geometry, LineString, MultiPolygon, Polygon


from .grid_proj import GridProj
from .utils import round_half_away as rnd_ha
from .vectaster import geographic_to_pixel, rasterize

logger = logging.getLogger(__name__)


class Color(NamedTuple):
    """Data class used to hold RGB colors"""
    red: float
    green: float
    blue: float


class ColorPalette(NamedTuple):
    """Color Palette Class"""
    lut: Sequence[Color]
    num_colors: int
    under_idx: int
    over_idx: int
    fill_idx: int

    # pylint: disable=invalid-name
    @classmethod
    def linear(cls, colors: Sequence[Color], anchors: Sequence[int] = None) -> Self:
        """Create a color palette by linearly interpolating between colors

        Args:
            colors (Sequence[Color]): A list of colors, first will be mapped to index 0,
                                      and last will be mapped to index 255.
            anchors (Sequence[int], optional): A list to define what index each color
                                      should be mapped to. Required: anchors[0] must equal 0,
                                      and anchor[-1] must 255. Defaults to None.

        Raises:
            ValueError: Raised when the length of the colors and anchors do not match

        Returns:
            ColorPalette: A color palette to be used with GeoImage
        """
        num = len(colors)
        if anchors is not None:
            if len(anchors) != num:
                raise ValueError('Colors and Anchors must be of the same length')
            xp = anchors
        else:
            xp = [rnd_ha(pos) for pos in np.linspace(0, 255, num=num)]
        lut = list((rnd_ha(r), rnd_ha(g), rnd_ha(b)) for (r, g, b) in
                   zip(*list(np.interp(range(256), xp, fp) for fp in np.array(colors).T)))
        return ColorPalette(lut, 256, 0, 255, 0)

    @classmethod
    def grey(cls, with_excludes: bool = True) -> Self:
        """Create a grey scale color palette

        Args:
            with_excludes (bool, optional): Indicate is the resulting color palette should have
                                            special colors for mapping values below/above min/max
                                            and fill values. Defaults to True.

        Returns:
            ColorPalette:  A grey scale color palette to be used with GeoImage
        """
        color_palette = cls.linear([(0, 0, 0), (255, 255, 255)])
        if with_excludes:
            lut = list(color_palette.lut)
            lut.extend((255, 142, 142) for _ in range(3))
            color_palette = ColorPalette(lut, 256, 256, 257, 258)
        return color_palette


class GeoImage():
    """Geographic Image Class"""

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
        """Method for building a geographical image from previously indexed data in a ndarray.
        Meaning that the data grid is has been mapped to indexed values that map to the provided
        color palette

        Args:
            proj (GridProj): Grid projection to be used for this geo image, must match data_grid
            index_array (np.ndarray): Data to be used as base layer, such as a temperature field,
                                      that has previously been mapped to color index.
            colors (ColorPalette | None, optional): The color palette used to map the index grid to
                                                    color. Defaults to None, in which case a grey
                                                    scale will be used.
            scale (int, optional): The height and width that a grid cell will be scaled to in the
                                   image. Defaults to 1.

        Returns:
            Self: GeoImage
        """
        if colors is None:
            colors = ColorPalette.grey()

        if scale != 1:
            index_array = np.repeat(np.repeat(index_array, scale, axis=1), scale, axis=0)
        rgb_array = np.array(colors.lut, np.uint8)[index_array]

        return GeoImage(proj, rgb_array, scale)

    @classmethod
    def from_data_grid(
        cls,
        proj: GridProj,
        data_array: np.ndarray,
        colors: ColorPalette | None = None,
        scale: int = 1,
        min_value: float = None,
        max_value: float = None,
        fill_value: float = None
    ) -> Self:
        """Method for building a geographical image from data in a ndarray.

        Args:
            proj (GridProj): Grid projection to be used for this geo image, must match data_grid
            data_array (np.ndarray): Data to be used as base layer, such as a temperature field.
            colors (ColorPalette | None, optional): The color palette used to map the data grid to
                                                    color. Defaults to None, in which case a grey
                                                    scale will be used.
            scale (int, optional): The height and width that a grid cell will be scaled to in the
                                   image. Defaults to 1.
            min_value (float, optional): The minimum value used for normalizing the data.
                                         Default to None, in which case use the min(data).
            max_value (float, optional): The maximum value used for normalizing the data.
                                         Default to None, in which case use the max(data).
            fill_value (float, optional): If specified this value will not be normalized.
                                         Default to None.

        Returns:
            Self: GeoImage
        """
        if colors is None:
            colors = ColorPalette.grey()
        norm_array = normalize(data_array, min_value, max_value, fill_value)
        index_array = scale_to_color_palette(norm_array, colors.num_colors)
        return GeoImage.from_index_grid(proj, index_array, colors, scale)

    @functools.cached_property
    def shape(self):
        """Image shape property

        Returns:
            tuple(int, int): The width and height of this GeoImage object
        """
        return self.rgb_array.shape

    @functools.cached_property
    def width(self):
        """Image width (first dim) property

        Returns:
            int: The width of this GeoImage object
        """
        return self.rgb_array.shape[0]

    @functools.cached_property
    def height(self):
        """Image height (second dim) property

        Returns:
            int: The height of this GeoImage object
        """
        return self.rgb_array.shape[1]

    def show(self):
        """A convenience method for showing the current state of the image"""
        image = Image.fromarray(np.flipud(np.transpose(self.rgb_array, [1, 0, 2])), mode='RGB')
        image.show()

    def draw_point(self, i: float, j: float, color: Color, geo: bool = True):
        """Draw a point onto the image, will only be one image cell and doesn't make use of scale.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
            geo (bool): Flag that indicates if the i,j are geographic (ie lon/lat) or pixel.
                        Defaults to True.
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
            geo (bool): Flag that indicates if the i,j's are geographic (ie lon/lat) or pixel.
                        Defaults to True.
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
            geo (bool): Indication that the shape is specified by geographic coordinates (lon/lat).
                        Defaults to True.

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
            geo (bool): Indication that the shape is specified by geographic coordinates (lon/lat).
                        Defaults to True.

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
            return
        else:
            raise TypeError(f'Passed shape (with type: {type(shape)}) in not currently supported')

        coords = rasterize(shape)

        for i, j in zip(*coords):
            if 0 <= i < self.width and 0 <= j < self.height:
                self.rgb_array[i, j] = color

    def set_pixel(self, i: float, j: float, color: Color, geo: bool = True):
        """Set all image cell associated with location specified by i, j to the passed color.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
            geo (bool): Flag that indicates if the i,j are geographic (ie lon/lat) or pixel.
                        Defaults to True.
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
            geo (bool): Flag that indicates if the shape vertices are geographic (ie lon/lat)
                        or pixel. Defaults to True.
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
            geo (bool): Flag that indicates if the shape vertices are geographic (ie lon/lat)
                        or pixel. Defaults to True.
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
            geo (bool): Flag that indicates if the shape vertices are geographic (ie lon/lat)
                        or pixel. Defaults to True.
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        coords = rasterize(shape, self.proj) if geo else rasterize(shape)
        for i_j in zip(*coords):
            self.outline_pixel(*i_j, color, geo=False)

    def draw_state(self, state: str, color: Color):
        """Draw state to image where all interior pixels are set to color

        Args:
            state (str): State name as string (Cap first letter of word, all other lower)
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        states = _get_states_json()
        self.draw_shape(states[state], color)

    def draw_state_boundary(self, state: str | Sequence[str], color: Color):
        """Draw state to image where all boundary pixels are set to color

        Args:
            state (str | Sequence[str]): State name or sequence of state names
                                         (Cap firs, lower rest)
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        states = _get_states_json()
        if state == 'All':
            for state_geo in states.values():
                self.draw_linestring(state_geo, color)
        elif isinstance(state, str):
            self.draw_linestring(states[state], color)
        else:
            for name in state:
                self.draw_linestring(states[name], color)


def normalize(
    array: np.ndarray,
    min_value: float = None,
    max_value: float = None,
    missing_value: float = None
) -> np.ndarray | np.ma.MaskedArray:
    """Normalize a data array, map the values in array to between [0, 1]

    Args:
        array (np.ndarray): Input data array
        min_value (float, optional): If provided, the minimum value to to be mapped.
                                     Will map to zero, and all values less will map to -1
                                     (-1 is out of range, but will be masked). Defaults to None.
        max_value (float, optional): If provided, the maximum value to to be mapped.
                                     Will map to 1, and all values greater will map to 2
                                     (2 is out of range, but will be masked). Defaults to None.
        missing_value (float, optional): If provided, the value representing fill, which will not
                                     be mapped to [0, 1]. Will map to np.nan, (NaN is not a valid
                                     float between [0, 1], but will be masked). Defaults to None.

    Returns:
        np.ndarray | np.ma.MaskedArray: If all data is mapped to [0, 1] the returned array will be
                                        an unmasked ndarray, else a masked array will be returned,
                                        masking all values not in range.
                                        Below min -> -1
                                        Above max ->  2
                                        Fill      -> np.nan
    """
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


def scale_to_color_palette(
        norm_array: np.ndarray | np.ma.MaskedArray,
        num_colors: int,
        with_under: bool = False,
        with_over: bool = False,
        with_fill: bool = False
) -> np.ndarray:
    """Take a normalized array and build index array relative to a color palette.

    Args:
        norm_array (np.ndarray | np.ma.MaskedArray): If norm_array is np.ndarray all values must be
                                                     between [0, 1], else if it is a masked array
                                                     all unmasked values must be between [0, 1] and
                                                     all masked values should be -1, 2 or np.nan.
        num_colors (int): The number of colors in the color palette that will be associated with the
                          output array
        with_under (bool, optional): Indicates of the associated color palette has a color used for
                                     values below 0, if so the index for that color is the one more
                                     than last valid index (typically num_colors).
                                     Defaults to False.
        with_over (bool, optional): Indicates of the associated color palette has a color used for
                                     values above 1, if so the index for that color is the one more
                                     than last valid index (typically num_colors+1).
                                     Defaults to False.
        with_fill (bool, optional): Indicates of the associated color palette as a color used for
                                     fill values, if so the index for that color is the one more
                                     than last valid index (typically num_colors+2).
                                     Defaults to False.

    Returns:
        np.ndarray: Returns an array with values that can be used with a color palette lookup table.
    """
    next_idx = num_colors
    under_idx = 0
    if with_under:
        under_idx = next_idx
        next_idx += 1
    over_idx = num_colors-1
    if with_over:
        over_idx = next_idx
        next_idx += 1
    bad_idx = 0
    if with_fill:
        bad_idx = next_idx

    with np.errstate(invalid="ignore"):
        array = (norm_array * (num_colors-1)).astype(int)

    if np.ma.is_masked(array):
        norm_array = norm_array.data

    array[norm_array == -1] = under_idx
    array[norm_array == 2] = over_idx
    array[np.isnan(norm_array)] = bad_idx

    return array


def _get_states_json() -> dict[str, Any]:
    """Load geojson of US states into a dict"""
    current_path = os.path.dirname(os.path.realpath(__file__))
    states_filename = os.path.join(current_path, 'resources', 'us_states.json')
    with open(states_filename, 'r', encoding='utf8') as file:
        states_json = json.load(file)
    states = {}
    for feature in states_json['features']:
        states[feature['properties']['NAME']] = from_geojson(json.dumps(feature))
    return states

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
import logging
import math
from typing import NamedTuple, Self

import numpy as np
from PIL import Image
from shapely import from_wkt, Geometry, LineString, Polygon


from .grid_proj import GridProj
from .vectaster import rasterize

logger = logging.getLogger(__name__)


class Color(NamedTuple):
    """Data class used to hold RGB colors"""
    red: float
    green: float
    blue: float


ColorPalette = list[Color]


class GeoImage():
    """AWS Utility Class"""

    def __init__(self, proj: GridProj, rgb_array: np.ndarray, scale: int = 1):
        self.proj = proj
        self.rgb_array = rgb_array
        self.scale = scale

    @classmethod
    def from_data_grid(
        cls,
        proj: GridProj,
        data_grid: np.ndarray,
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
        min_ = np.min(data_grid)
        max_ = np.max(data_grid)

        if colors is None:
            colors = _get_grey_scale()

        step = 255./(max_-min_) if min_ != max_ else 0
        new_shape = [dim * scale for dim in data_grid.shape]+[3]
        rgb_array = np.zeros(new_shape, dtype=np.uint8)
        for idx, x in np.ndenumerate(data_grid):
            color = colors[255] if x == max_ else colors[int((x-min_)*step)]
            i, j = [i*scale for i in idx]
            rgb_array[i:i+scale, j:j+scale] = color
        return GeoImage(proj, rgb_array, scale)

    def show(self):
        """A convenience method for showing the current state of the image"""
        image = Image.fromarray(self.rgb_array, mode='RGB')
        image.show()

    def draw_point(self, i: float, j: float, color: Color):
        """Draw a point onto the image, will only be one image cell and doesn't make use of scale.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        self.rgb_array[int(i*self.scale), int(j*self.scale)] = color

    def draw_line_seg(  # pylint: disable=too-many-arguments
            self,
            i_1: float, j_1: float,
            i_2: float, j_2: float,
            color: Color
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
        self.draw_shape(f'LINESTRING ({i_1} {j_1}, {i_2} {j_2})', color)

    def draw_shape(self, shape: Geometry, color: Color):
        """Draw a shape onto the image, points and lines will only be on image cell wide
        and polygon will be filled, doesn't make use of scale.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255

        Raises:
            TypeError: Raised when the passed shape in not of a supported type
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        if isinstance(shape, LineString):
            vertices = [(int(i*self.scale), int(j*self.scale)) for i, j in shape.coords]
            shape = LineString(vertices)
        elif isinstance(shape, Polygon):
            outer = [(int(i*self.scale), int(j*self.scale)) for i, j in shape.exterior.coords]
            inner = [[(int(i*self.scale), int(j*self.scale)) for i, j in inner.coords]
                     for inner in shape.interiors]
            shape = Polygon(outer, inner)
        else:
            raise TypeError('Passed shape in not currently supported')

        coords = rasterize(shape)
        for i_j in zip(*coords):
            self.rgb_array[*i_j] = color

    def set_pixel(self, i: float, j: float, color: Color):
        """Set all image cell associated with location specified by i, j to the passed color.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        i = math.floor(i)*self.scale
        j = math.floor(j)*self.scale
        self.rgb_array[i:i+self.scale, j:j+self.scale] = color

    def set_pixel_for_shape(self, shape: Geometry, color: Color):
        """Set all image cell associated with geometry to the specified color.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        coords = rasterize(shape)
        for i_j in zip(*coords):
            self.set_pixel(*i_j, color)

    def outline_pixel(self, i: float, j: float, color: Color):
        """Set the image cell associated with outside edge of location specified by i, j
        to the passed color.

        Args:
            i (float): Location of the point, corresponding to the first dim
            j (float): Location of the point, corresponding to the second dim
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        i = math.floor(i)*self.scale
        j = math.floor(j)*self.scale
        self.rgb_array[i:i+self.scale, j] = color
        self.rgb_array[i:i+self.scale, j+self.scale-1] = color
        self.rgb_array[i, j:j+self.scale] = color
        self.rgb_array[i+self.scale-1, j:j+self.scale] = color

    def outline_pixel_for_shape(self, shape, color):
        """Set all image cell associated outside edge of pixels associated with geometry
          to the specified color.

        Args:
            shape (Geometry): A Shapely geometry
            color (Color): RGB value as a tuple of three values between 0 and 255
        """
        if isinstance(shape, str):
            shape = from_wkt(shape)

        coords = rasterize(shape)
        for i_j in zip(*coords):
            self.outline_pixel(*i_j, color)


@functools.cache
def _get_grey_scale():
    return [(x, x, x) for x in range(0, 256)]

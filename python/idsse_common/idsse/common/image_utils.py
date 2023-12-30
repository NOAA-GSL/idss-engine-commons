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
import numpy as np

from numpy import ndarray
from PIL import Image
from shapely import from_wkt, Geometry, LineString, Polygon
from typing import List, NamedTuple, Self

from .grid_proj import GridProj
from .vectaster import rasterize

logger = logging.getLogger(__name__)


class Color(NamedTuple):
    """Data class used to hold RGB colors"""
    red: float
    green: float
    blue: float


ColorPalette = List[Color]


class GeoImage():
    """AWS Utility Class"""

    def __init__(self, proj: GridProj, rgb_array: ndarray, scale: int = 1):
        self.proj = proj
        self.rgb_array = rgb_array
        self.scale = scale

    @classmethod
    def from_data_grid(cls,
                       proj: GridProj,
                       data_grid: ndarray,
                       colors: None | ColorPalette = None,
                       scale: int = 1) -> Self:
        min = np.min(data_grid)
        max = np.max(data_grid)

        if colors is None:
            colors = _get_grey_scale()

        step = 255./(max-min)
        new_shape = [dim * scale for dim in data_grid.shape]+[3]
        rgb_array = np.zeros(new_shape, dtype=np.uint8)
        for idx, x in np.ndenumerate(data_grid):
            color = colors[255] if x == max else colors[int((x-min)*step)]
            i, j = [i*scale for i in idx]
            rgb_array[i:i+scale, j:j+scale] = color
        print(rgb_array)
        print(rgb_array.shape)
        rgb_array[10, 10] = 0
        return GeoImage(proj, rgb_array, scale)

    def show(self):
        image = Image.fromarray(self.rgb_array, mode='RGB')
        image.show()

    def draw_point(self, i, j, color):
        print(i, j)
        self.rgb_array[int(i*self.scale), int(j*self.scale)] = color

    def draw_line_seg(self, i1, j1, i2, j2, color):
        self.draw_shape(f'LINESTRING ({i1} {j1}, {i2} {j2})', color)

    def draw_shape(self, shape: Geometry, color):
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
            raise ValueError('Passed shape in not currently supported')

        coords = rasterize(shape)
        for i_j in zip(*coords):
            print((i_j))
            self.rgb_array[*i_j] = color

    def set_pixel(self, i, j, color):
        i *= self.scale
        j *= self.scale
        self.rgb_array[i:i+self.scale, j:j+self.scale] = color

    def outline_pixel(self, i, j, color):
        i *= self.scale
        j *= self.scale
        self.rgb_array[i:i+self.scale, j] = color
        self.rgb_array[i:i+self.scale, j+self.scale-1] = color
        self.rgb_array[i, j:j+self.scale] = color
        self.rgb_array[i+self.scale-1, j:j+self.scale] = color


@functools.cache
def _get_grey_scale():
    return [(x, x, x) for x in range(0, 256)]
    # step = 1./255.
    # colors = [((step*x, )*3) for x in range(0, 255)]
    # colors.append((1., 1., 1.))
    # return colors

#         input = numpy_image

# np.uint8 -> converts to integers

# convert('RGB') -> converts to RGB

# Image.fromarray -> returns an image object

#   from PIL import Image
#   import numpy as np

#   PIL_image = Image.fromarray(np.uint8(numpy_image)).convert('RGB')

#   PIL_image = Image.fromarray(numpy_image.astype('uint8'), 'RGB')

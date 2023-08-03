"""Module that wraps pyproj (cartographic/geodetic) library and transforms objects into other data forms"""
# -------------------------------------------------------------------------------
# Created on Mon Jul 31 2023
#
# Copyright (c) 2023 Colorado State University. All rights reserved. (1)
#
# Contributors:
#     Mackenzie Grimes (1)
#
# -------------------------------------------------------------------------------
# pylint: disable=invalid-name

from typing import Self, Tuple, Union, Any, Optional
from enum import Enum, auto
from math import floor

from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection


class PixelRounding(Enum):
    """Transformations to apply to calculated pixels when casting to ints"""
    ROUND = auto()
    FLOOR = auto()


class GridProj:
    """Wrapper for pyproj instance with methods to convert to and from geographic coordinates, pixels, etc."""
    def __init__(self,
                 crs: CRS,
                 latitude: float,
                 longitude: float,
                 width: float,
                 height: float,
                 dx: float,
                 dy: Optional[float] = None):
        # pylint: disable=too-many-arguments,unpacking-non-sequence
        self._trans = Transformer.from_crs(crs.geodetic_crs, crs)
        self._x_offset, self._y_offset = self._trans.transform(longitude, latitude)
        self._w = width
        self._h = height
        self._dx = dx
        self._dy = dy if dy else dx

    @classmethod
    def from_proj_grid_spec(cls, proj_string: str, grid_string: str) -> Self:
        """ Create GridProj instance from projection grid specs

        Args:
            proj_string (str): pyproj projection string
            grid_string (str): Grid string

        Returns:
            Self: New instance of GridProj which can then be converted to any format
        """
        crs = CRS.from_proj4(proj_string)
        grid_args = {
            key[1:]: float(value)
            for key, value in (
                pair.split('=') for pair in grid_string.split(' ')
            )
        }
        return GridProj(crs,
                        grid_args['lat_ll'], grid_args['lon_ll'],
                        int(grid_args['w']), int(grid_args['h']),
                        grid_args['dx'], grid_args['dy'])

    def map_proj_to_pixel(self, x, y) -> Tuple[float, float]:
        """Map projection to a pixel"""
        return self.map_geo_to_pixel(*self._trans.transform(x, y))  # pylint: disable=not-an-iterable

    def map_pixel_to_proj(self, x: float, y: float) -> Tuple[Any, Any]:
        """Map pixel to a projection"""
        return self._trans.transform(*self.map_pixel_to_geo(x, y), direction=TransformDirection.INVERSE)

    def map_proj_to_geo(self, x, y) -> Tuple[float, float]:
        """Map projection to geographic coordinates"""
        return self._trans.transform(x, y)

    def map_pixel_to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Map pixel to geographic coordinates"""
        return x * self._dx + self._x_offset, y * self._dy + self._y_offset

    def map_geo_to_proj(self, x: float, y: float) -> Tuple[Any, Any]:
        """Map geographic coordinates to a projection"""
        return self._trans.transform(x, y, direction=TransformDirection.INVERSE)

    def map_geo_to_pixel(
        self, x: float,
        y: float,
        rounding: Optional[PixelRounding] = None
    ) -> Tuple[Union[int, float], Union[int, float]]:
        """Map geographic coordinates to a pixel

        Pixels are only identified by whole numbers when graphically rendered,
        so the transformed numerical values (floats) can be safely rounded to ints

        Args:
            x (float): x geographic coordinate
            y (float): y geographic coordinate
            rounding (Optional[PixelRounding]):
                ROUND to apply round() to pixel values, FLOOR to apply math.floor().
                By default, pixels are not rounded and will be returned as floats

        Returns:
            Tuple[Union[int, float], Union[int, float]):
                x, y values for pixel, rounded to ints if rounding parameter passed, otherwise floats
        """
        pixel_x = (x - self._x_offset) / self._dx
        pixel_y = (y - self._y_offset) / self._dy

        if rounding is PixelRounding.ROUND:
            return (round(pixel_x), round(pixel_y))
        if rounding is PixelRounding.FLOOR:
            return (floor(pixel_x), floor(pixel_y))
        return (pixel_x, pixel_y)

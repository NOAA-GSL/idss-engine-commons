"""Module that wraps pyproj (cartographic) library and transforms objects into other data forms"""
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
from enum import Enum
import math

from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection

from .utils import round_half_away


Pixel = Tuple[Union[int, float], Union[int, float]]


class RoundingMethod(Enum):
    """Transformations to apply to calculated pixel values when casting to ints"""
    ROUND = 'ROUND'
    FLOOR = 'FLOOR'


class GridProj:
    """
    Wrapper for pyproj instance with methods to convert
    to and from geographic coordinates, pixels, etc.
    """
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


    def _round_pixel_maybe(
        self,
        pixel: Tuple[float, float],
        rounding: Optional[Union[str, RoundingMethod]] = None,
        precision: int = 0
    ) -> Pixel:
        """Round pixel values if caller requested, or return unchanged if no rounding passed"""
        x, y = pixel
        # cast str to RoundingMethod enum
        if isinstance(rounding, str):
            rounding = RoundingMethod[rounding.upper()]

        if rounding is RoundingMethod.ROUND:
            return (round_half_away(x, precision), round_half_away(y, precision))
        if rounding is RoundingMethod.FLOOR:
            return (math.floor(x), math.floor(y))
        return x, y

    def map_proj_to_pixel(
        self,
        x: float,
        y: float,
        rounding: Optional[Union[str, RoundingMethod]] = None,
        precision: int = 0
    ) -> Pixel:
        """Map projection to a pixel.

        Args:
            x (float): x geographic coordinate
            y (float): y geographic coordinate
            rounding (Optional[Union[str, RoundingMethod]]):
                ROUND to apply round_half_away() to pixel values,
                FLOOR to apply math.floor().
                Supports RoundingMethod enum value or str value (case insensitive).
                By default, pixels are not rounded and will be returned as floats
            precision (int): number of decimal places to round to. If rounding parameter
                is None, this will be ignored

        Returns:
            Pixel: x, y values of pixel, rounded to ints if rounding is passed, otherwise floats
        """
        # pylint: disable=not-an-iterable
        return self.map_geo_to_pixel(
            *self._trans.transform(x, y),
            rounding=rounding,
            precision=precision
        )

    def map_pixel_to_proj(self, x: float, y: float) -> Tuple[float, float]:
        """Map pixel to a projection"""
        return self._trans.transform(
            *self.map_pixel_to_geo(x, y),
            direction=TransformDirection.INVERSE
        )

    def map_proj_to_geo(self, x, y) -> Tuple[float, float]:
        """Map projection to geographic coordinates"""
        return self._trans.transform(x, y)

    def map_pixel_to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Map pixel to geographic coordinates"""
        return x * self._dx + self._x_offset, y * self._dy + self._y_offset

    def map_geo_to_proj(self, x: float, y: float) -> Tuple[float, float]:
        """Map geographic coordinates to a projection"""
        return self._trans.transform(x, y, direction=TransformDirection.INVERSE)

    def map_geo_to_pixel(
        self,
        x: float,
        y: float,
        rounding: Optional[Union[str, RoundingMethod]] = None,
        precision: int = 0
    ) -> Pixel:
        """Map geographic coordinates to pixel x and y

        Args:
            x (float): x geographic coordinate
            y (float): y geographic coordinate
            rounding (Optional[Union[str, RoundingMethod]]):
                ROUND to apply round_half_away() to pixel values,
                FLOOR to apply math.floor().
                Supports RoundingMethod enum value or str value (case insensitive).
                By default, pixels are not rounded and will be returned as floats
            precision (int): number of decimal places to round to. If rounding parameter
                is None, this will be ignored

        Returns:
            Pixel: x, y values of pixel, rounded to ints if rounding passed, otherwise floats
        """
        i: float = (x - self._x_offset) / self._dx
        j: float = (y - self._y_offset) / self._dy
        return self._round_pixel_maybe((i, j), rounding, precision)

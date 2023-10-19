"""Module that wraps pyproj (cartographic) library and transforms objects into other data forms"""
# ----------------------------------------------------------------------------------
# Created on Mon Jul 31 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#    Mackenzie Grimes (2)
#    Geary Layne (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=invalid-name
# cspell:word fliplr, flipud

from typing import Self, Tuple, Union, Optional
from enum import Enum
import math

from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection

from .utils import round_half_away


Pixel = Tuple[Union[int, float], Union[int, float]]


class RoundingMethod(Enum):
    """Transformations indicators to be applied to pixel values when casting to ints"""
    ROUND = 'ROUND'
    FLOOR = 'FLOOR'

class Flip(Enum):
    """Flip axis indicators to be applied flipping pixel orientation"""
    BOTH = 'BOTH'
    HORIZONTAL = 'HORIZONTAL'
    VERTICAL = 'VERTICAL'

class GridProj:
    """
    Wrapper for pyproj instance with methods to convert
    to and from geographic coordinates, pixels, etc.
    """
    def __init__(self,
                 crs: CRS,
                 lower_left_lat: float,
                 lower_left_lon: float,
                 width: float,
                 height: float,
                 dx: float,
                 dy: Optional[float] = None):
        # pylint: disable=too-many-arguments,unpacking-non-sequence
        self._trans = Transformer.from_crs(crs.geodetic_crs, crs)
        self._x_offset = 0
        self._y_offset = 0
        if lower_left_lat is not None:
            self._x_offset, self._y_offset = self._trans.transform(lower_left_lon, lower_left_lat)
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
        if 'lat_ll' not in grid_args:
            grid_args['lat_ll'] = None
            grid_args['lon_ll'] = None
        return GridProj(crs,
                        grid_args['lat_ll'], grid_args['lon_ll'],
                        int(grid_args['w']), int(grid_args['h']),
                        grid_args['dx'], grid_args['dy'])

    @property
    def width(self):
        """Provides access grid space width"""
        return self._w

    @property
    def height(self):
        """Provides access grid space height"""
        return self._h

    @property
    def shape(self):
        """Provides access grid space shape: (width, height)"""
        return self._w, self._h

    def flip(self, flip: Flip = Flip.BOTH):
        """Reverse the order of pixels for a given orientation

        Args:
            flip (Flip): The default, flip=BOTH, will flip over both axes.
        """
        if flip is Flip.BOTH:
            self._x_offset, self._y_offset = self.map_pixel_to_crs(self.width, self.height)
            self._dx *= -1
            self._dy *= -1
        elif flip is Flip.HORIZONTAL:
            self._x_offset, _ = self.map_pixel_to_crs(self.width, 0)
            self._dx *= -1
        elif flip is Flip.VERTICAL:
            _, self._y_offset = self.map_pixel_to_crs(0, self.height)
            self._dy *= -1

    def fliplr(self):
        """Reverse the order of the pixels left to right"""
        self.flip(Flip.HORIZONTAL)

    def flipud(self):
        """Reverse the order of the pixels up to down"""
        self.flip(Flip.VERTICAL)

    def map_geo_to_pixel(
        self,
        lon: float,
        lat: float,
        rounding: Optional[Union[str, RoundingMethod]] = None,
        precision: int = 0
    ) -> Pixel:
        """Map projection to a pixel.

        Args:
            lon (float): x geographic coordinate
            lat (float): y geographic coordinate
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
        return self.map_crs_to_pixel(
            *self._trans.transform(lon, lat),
            rounding=rounding,
            precision=precision
        )

    def map_pixel_to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Map pixel x,y to a projection

        Args:
            x (float): x coordinate in pixel space
            y (float): y coordinate in pixel space

        Returns:
            Tuple[float, float]: Geographic coordinate as lon,lat
        """
        return self._trans.transform(
            *self.map_pixel_to_crs(x, y),
            direction=TransformDirection.INVERSE
        )

    def map_geo_to_crs(self, lon: float, lat: float) -> Tuple[float, float]:
        """Map geographic coordinate (lon, lat) to CRS

        Args:
            lon (float): x geographic coordinate
            lat (float): y geographic coordinate

        Returns:
            Tuple[float, float]: Coordinate Reference System
        """
        return self._trans.transform(lon, lat)

    def map_pixel_to_crs(self, x: float, y: float) -> Tuple[float, float]:
        """Map pixel space (x,y) to Coordinate Reference System

        Args:
            x (float): x coordinate in pixel space
            y (float): y coordinate in pixel space

        Returns:
            Tuple[float, float]: Coordinate Reference System coordinate
        """
        return x * self._dx + self._x_offset, y * self._dy + self._y_offset

    def map_crs_to_geo(self, x: float, y: float) -> Tuple[float, float]:
        """Map Coordinate Reference System (x,y) to Geographical space (lon,lat)

        Args:
            x (float): x coordinate in CRS space
            y (float): y coordinate in CRS space

        Returns:
            Tuple[float, float]: Geographic coordinate as lon,lat
        """
        return self._trans.transform(x, y, direction=TransformDirection.INVERSE)

    def map_crs_to_pixel(
        self,
        x: float,
        y: float,
        rounding: Optional[Union[str, RoundingMethod]] = None,
        precision: int = 0
    ) -> Pixel:
        """Map Coordinate Reference System (x,y) coordinates to pixel x and y

        Args:
            x (float): x CRS coordinate
            y (float): y CRS coordinate
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

    @staticmethod
    def _round_pixel_maybe(
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

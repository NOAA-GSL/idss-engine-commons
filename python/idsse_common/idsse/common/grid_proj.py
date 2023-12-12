"""Module that wraps pyproj (cartographic) library and transforms objects into other data forms"""
# ----------------------------------------------------------------------------------
# Created on Mon Jul 31 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Mackenzie Grimes (2)
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=invalid-name
# cspell:word fliplr, flipud

from typing import Self, Tuple, Union, Optional, Sequence, TypeVar, Iterable
from enum import Enum
import math

import numpy as np
from pyproj import CRS, Transformer
from pyproj.enums import TransformDirection

from .utils import round_half_away

# type hints
Scalar = Union[int, float]
ScalarPair = Tuple[Scalar, Scalar]
ScalarArray = Sequence[Scalar]
Coordinate = Union[Scalar, ScalarPair, ScalarArray, np.ndarray]
CoordinatePair = Tuple[Coordinate, Coordinate]

T = TypeVar('T', Scalar, ScalarPair, ScalarArray, np.ndarray)

class RoundingMethod(Enum):
    """Transformations indicators to be applied to pixel values when casting to ints"""
    ROUND = 'ROUND'
    FLOOR = 'FLOOR'


RoundingParam = Union[str, RoundingMethod]


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
                 lower_left_lat: Optional[float],
                 lower_left_lon: Optional[float],
                 width: float,
                 height: float,
                 dx: float,
                 dy: Optional[float] = None):
        # pylint: disable=too-many-arguments,unpacking-non-sequence
        self._trans = Transformer.from_crs(crs.geodetic_crs, crs)
        self._x_offset = 0.0
        self._y_offset = 0.0
        if lower_left_lat is not None and lower_left_lon is not None:
            self._x_offset, self._y_offset = self._transform(lower_left_lon, lower_left_lat)
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

    def _transform(
        self,
        xx: T,
        yy: T,
        direction: Union[TransformDirection, str] = TransformDirection.FORWARD
    ) -> Tuple[T, T]:
        """Transform any x coordinate/array and y coordinate/array to a Tuple of the same types,
        converted into the GridProj's coordination system.

        Wrapper for Transformer.transform() with more specific type hinting than pyproj (Any)
        """
        return self._trans.transform(xx, yy, direction=direction)

    def map_geo_to_pixel(
        self,
        lon: T,
        lat: T,
        rounding: Optional[RoundingParam] = None,
        precision: int = 0
    ) -> Tuple[T, T]:
        """Map geographic coordinates to a pixel.

        Args:
            lon (T): single x geographic coordinate, or array of all x coordinates
            lat (T): single y geographic coordinate, or array of all y coordinates
            rounding (Optional[RoundingParam]):
                ROUND to apply round_half_away() to pixel values,
                FLOOR to apply math.floor().
                Supports RoundingMethod enum value or str value (case insensitive).
                By default, float pixels are not rounded and will be returned as floats
            precision (int): number of decimal places to round to. If rounding parameter
                is None, this will be ignored

        Returns:
            T: x, y values (or arrays) of pixel, matching the type passed as lon/lat. Values are
                rounded to ints if rounding arg is passed, otherwise left as floats
        """
        crs_coordinates = self.map_geo_to_crs(lon, lat)
        # pylint: disable=not-an-iterable
        return self.map_crs_to_pixel(
            *crs_coordinates,
            rounding=rounding,
            precision=precision
        )

    def map_pixel_to_geo(self, x: T, y: T) -> Tuple[T, T]:
        """Map one or more pixel(s) x,y to a projection

        Args:
            x (ScalarOrArray): x coordinate (or array) in pixel space
            y (ScalarOrArray): y coordinate (or array) in pixel space

        Returns:
            Tuple[ScalarOrArray, ScalarOrArray]: Single geographic coordinate as lon,lat, or
                entire array of lat,lon pairs if arrays were passed
        """
        crs_coordinates = self.map_pixel_to_crs(x, y)
        return self.map_crs_to_geo(*crs_coordinates)

    def map_geo_to_crs(self, lon: T, lat: T) -> Tuple[T, T]:
        """Map geographic coordinate (lon, lat) to CRS

        Args:
            lon (float): x geographic coordinate
            lat (float): y geographic coordinate

        Returns:
            Tuple[float, float]: Coordinate Reference System
        """
        return self._transform(lon, lat)

    def map_pixel_to_crs(self, x: T, y: T) -> Tuple[T, T]:
        """Map pixel space (x,y) to Coordinate Reference System

        Args:
            x (Coordinate): x coordinate (or array) in pixel space
            y (Coordinate): y coordinate (or array) in pixel space

        Returns:
            Tuple[Coordinate, Coordinate]: Coordinate Reference System coordinate
        """
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            return ([], [])  # TODO

        if isinstance(x, Iterable) and isinstance(y, Iterable):
            return ([], [])  # TODO

        if isinstance(x, Scalar) and isinstance(y, Scalar):
            return x * self._dx + self._x_offset, y * self._dy + self._y_offset

        raise TypeError(
            f'Cannot transpose pixel values of ({type(x).__name__})({type(y).__name__}) to CRS'
        )

    def map_crs_to_geo(self, x: T, y: T) -> Tuple[T, T]:
        """Map Coordinate Reference System (x,y) to Geographical space (lon,lat)

        Args:
            x (float): x coordinate in CRS space
            y (float): y coordinate in CRS space

        Returns:
            Tuple[float, float]: Geographic coordinate as lon,lat
        """
        return self._transform(x, y, direction=TransformDirection.INVERSE)

    def map_crs_to_pixel(
        self,
        x: T,
        y: T,
        rounding: Optional[RoundingParam] = None,
        precision: int = 0
    ) -> Tuple[T, T]:
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

        Raises:
            TypeError: if x or y CRS values are type not supported by Coordinate
                (a.k.a. int | float | Sequence[int | float] | np.ndarray)
        """
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            # TODO: somehow pass arrays directly to numpy to convert
            return np.transpose(np.array(x, y))

        if isinstance(x, Iterable) and isinstance(y, Iterable):
            pixel_array: Sequence[Tuple[Scalar]] = []

            # Combine array of x coordinates with array of y coordinates to make list of
            # CRS x, y pairs. Transform each CRS pair to a pixel, then split back into list
            # of x, y pairs (but now dimensions are pixel rather than CRS)
            for crs_coordinate in zip(x, y):
                pixel: ScalarPair = self.map_crs_to_pixel(*crs_coordinate, rounding, precision)
                pixel_array.append(pixel)

            return tuple(zip(*pixel_array))

        if isinstance(x, Scalar) and isinstance(y, Scalar):
            # single CRS coordinate passed (base case)
            i: float = (x - self._x_offset) / self._dx
            j: float = (y - self._y_offset) / self._dy
            return self._round_pixel_maybe((i, j), rounding, precision)

        raise TypeError(
            f'Cannot transpose CRS values of ({type(x).__name__})({type(y).__name__}) to pixel'
        )


    @staticmethod
    def _round_pixel_maybe(
        pixel: ScalarPair,
        rounding: Optional[Union[str, RoundingMethod]] = None,
        precision: int = 0
    ) -> ScalarPair:
        """Round pixel values if caller requested, or return unchanged if no rounding passed"""
        x, y = pixel

        if isinstance(rounding, str):  # cast str to RoundingMethod enum
            rounding = RoundingMethod[rounding.upper()]

        if rounding is RoundingMethod.ROUND:
            return (round_half_away(x, precision), round_half_away(y, precision))
        if rounding is RoundingMethod.FLOOR:
            return (math.floor(x), math.floor(y))

        return pixel  # rounding is None, or some unsupported rounding method

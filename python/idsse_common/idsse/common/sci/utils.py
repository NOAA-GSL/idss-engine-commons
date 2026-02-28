"""A collection of useful classes and utility functions involving scientific libraries"""

# -----------------------------------------------------------------------------------
# Created on Wed Jan 24 2024
#
# Copyright (c) 2024 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2024 Colorado State University. All rights reserved.             (2)
#
# Contributors:
#    Mackenzie Grimes (2)
#
# ------------------------------------------------------------------------------------

import logging
from collections.abc import Sequence
from datetime import datetime, UTC
from typing import NewType

import numpy

# import shapely

logger = logging.getLogger(__name__)

# type aliases
Pixel = NewType("Pixel", Sequence[int])
Coord = NewType("Coord", Sequence[float])
Coords = NewType("Coords", Sequence[Coord])


def coordinate_pairs_to_axes(
    points: Sequence[Pixel] | Coords, dtype: numpy.dtype | None = None
) -> tuple[numpy.ndarray]:
    """Convert a list of (x,y) tuples to a tuple of values on the x axis and values on the y axis,
        represented as numpy arrays.

    Args:
        points (Sequence[Pixel]): list of (x,y) coordinates
        dtype: (numpy.dtype | None): data type of resulting numpy arrays. Default: None

    Returns:
        tuple[numpy.ndarray]: Same coordinates but restructured
            as all coordinates on x axis, followed by all coordinates on y axis
    """
    return tuple(numpy.array(dim_coord, dtype=dtype) for dim_coord in tuple(zip(*points)))


def numpy_datetime_to_datetime(np_datetime: numpy.datetime64, tz=UTC) -> datetime:
    """Convert a numpy datetime64 to a timezone-aware Python `datetime` object.

    Args:
        np_datetime (numpy.datetime64): a numpy datetime, which will appear as a 0-dimension array
            with a single float value. E.g. str representation is `array(123456, datetime64['ns'])`.
        tz (optional, datetime.tz): the assumed timezone of the float value. Defaults to `UTC`
    """
    timestamp = (np_datetime - numpy.datetime64("1970-01-01")) / numpy.timedelta64(1, "s")
    return datetime.fromtimestamp(timestamp, tz=tz)

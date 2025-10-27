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
from typing import NewType
from datetime import datetime, timezone, UTC

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


def numpy_datetime_to_datetime(
    _datetime: numpy.datetime64, dtype: numpy.dtype, tz: timezone = UTC
) -> datetime:
    """Convert a `numpy.datetime64` object to a timezone-aware Python `datetime`.

    Args:
        _datetime (numpy.datetime64): a numpy.datetime64 object
        dtype (numpy.dtype): the dtype from the numpy datetime (usually `datetime64[ns]`)
        tz (timezone, optional): Python timezone to assume, as numpy datetimes are timezone-naive.
            Defaults to `datetime.UTC`.

    Returns:
        datetime: A timezone-aware Python `datetime` object.
    """
    # dt_parse(f'{np.datetime_as_string(file.valid_time)}Z')
    time_since_epoch = _datetime - numpy.datetime64(0, "s")
    if str(dtype).endswith("[ns]"):
        # numpy units are nanoseconds, which Python datetime cannot handle; convert to seconds
        timestamp = time_since_epoch / numpy.timedelta64(1, "s")
    else:
        timestamp = time_since_epoch
    return datetime.fromtimestamp(timestamp).replace(tzinfo=tz)

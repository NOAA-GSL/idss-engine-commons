"""A collection of useful classes and utility functions involving scientific libraries"""
# -----------------------------------------------------------------------------------
# Created on Wed Jan 24 2024
#
# Copyright (c) 2024 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2024 Colorado State University. All rights reserved.             (2)
#
# Contributors:
#    Mackenzie Grimes
#
# -----------------------------------------------------------------------------------

import copy
import logging
import math
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import NewType, Sequence
from uuid import UUID

import numpy
# import shapely

logger = logging.getLogger(__name__)

# type aliases
Pixel = NewType('Pixel', Sequence[int])
Coord = NewType('Coord', Sequence[float])
Coords = NewType('Coords', Sequence[Coord])


def split_coordinate_pairs(points: Sequence[Pixel], dtype = numpy.int64) -> tuple[numpy.ndarray]:
    """Convert a list of (x,y) tuples to a tuple of x values (as numpy array) and y
    values (numpy array).

    Args:
        points (Sequence[Pixel]): list of (x,y) coordinates
        dtype: (numpy.dtype, optional): data type of resulting numpy arrays. Default: int64

    Returns:
        Tuple[numpy.ndarray]: Same coordinates but restructured
    """
    return tuple(numpy.array(dim_coord, dtype=dtype) for dim_coord in tuple(zip(*points)))

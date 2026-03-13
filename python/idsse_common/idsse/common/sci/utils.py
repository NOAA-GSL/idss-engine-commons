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
import math
from collections.abc import Sequence
from typing import NewType

import numpy as np

from idsse.common.utils import RoundingMethod, RoundingParam

logger = logging.getLogger(__name__)

# type aliases
Scalar = int | float | np.integer | np.float64
Pixel = NewType("Pixel", Sequence[int])
Coord = NewType("Coord", Sequence[float])
Coords = NewType("Coords", Sequence[Coord])


def coordinate_pairs_to_axes(
    points: Sequence[Pixel] | Coords, dtype: np.dtype | None = None
) -> tuple[np.ndarray]:
    """Convert a list of (x,y) tuples to a tuple of values on the x axis and values on the y axis,
        represented as numpy arrays.

    Args:
        points (Sequence[Pixel]): list of (x,y) coordinates
        dtype: (numpy.dtype | None): data type of resulting numpy arrays. Default: None

    Returns:
        tuple[numpy.ndarray]: Same coordinates but restructured
            as all coordinates on x axis, followed by all coordinates on y axis
    """
    return tuple(np.stack(points).transpose().astype(dtype))


def round_scalar(value: Scalar, rounding: RoundingParam) -> Scalar:
    """Round a Python int/float or numpy int/float, preserving the original type as much
    as possible (e.g. numpy.float32 is rounded and returns numpy.integer)"""
    if isinstance(rounding, str):  # cast string rounding to constant RoundingMethod
        rounding = RoundingMethod.from_str(rounding)

    is_py_scalar = isinstance(value, (int, float))

    if rounding == RoundingMethod.ROUND:
        return round(value) if is_py_scalar else value.astype(int)
    if rounding == RoundingMethod.FLOOR:
        return math.floor(value) if is_py_scalar else np.floor(value)
    if rounding == RoundingMethod.CEIL:
        return math.ceil(value) if is_py_scalar else np.ceil(value)

    raise ValueError(f"Unsupported rounding method: {rounding}")

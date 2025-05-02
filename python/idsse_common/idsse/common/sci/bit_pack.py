"""Utility module for packing data"""

# ----------------------------------------------------------------------------------
# Created on Thu Dec 14 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Geary Layne (1)
#     Paul Hamer (2)
#
# ----------------------------------------------------------------------------------

from enum import IntEnum
from typing import NamedTuple
import numpy


class PackType(IntEnum):
    """Enumerated type used to indicate if data is packed into a byte or short (16 bit)"""

    BYTE = 8
    SHORT = 16


class PackInfo(NamedTuple):
    """Data class used to hold packing info"""

    type: PackType
    scale: float
    offset: float


class PackData(NamedTuple):
    """Data class used to hold packed data and the corresponding packing info"""

    type: PackType
    scale: float
    offset: float
    data: list | numpy.ndarray


def get_min_max(data: list | numpy.ndarray) -> tuple[float, float]:
    """Get the minimum and maximum from the numpy array or list. Testing showed (on a mac)
    that numpy was faster...

    Args:
        data (list | numpy.ndarray): Input data, either in list form
                                        (e.g. list[list[float]] for 2D) or as a numpy array
    Raises:
        TypeError: If the arguments for the call to the function are invalid
    Returns:
        tuple[float, float]: The minimum, maximum from the supplied argument
    """
    if isinstance(data, list):
        arr = numpy.array(data).ravel(order="K")
        return numpy.min(arr), numpy.max(arr)
    data.ravel(order="K")
    return numpy.min(data), numpy.max(data)


def get_pack_info(
    min_value: float, max_value: float, decimals: int = None, pack_type: PackType = None
) -> PackInfo:
    """Retrieve appropriate packing info based on min/max values and
    either decimals of precision or pack type.

    Args:
        min_value (float): The minimum value of the data to be packed
        max_value (float): The maximum value of the data to be packed.
        decimals (int, optional): The number of decimal places of precision being requested.
                                  If the decimals is None, it indicates the PackType should
                                  be used. Defaults to None.
        pack_type (PackType, optional): The pack type (byte or short) being requested.
                                        If the pack_type is None, it indicate that decimals
                                        of precision should be used. Defaults to None.

    Raises:
        ValueError: If one and only one of decimals aor pack_type aren't provided, or
                    if not appropriate packing type can be found.

    Returns:
        PackInfo: The determined packing info, including packing type (byte or short), and
                  scale and offset.
    """
    if decimals is None and pack_type is None:
        raise ValueError("Either decimals or pack_type must be non None")

    if decimals is not None and pack_type is not None:
        raise ValueError("Either decimals or pack_type must be non None, but not both")

    if pack_type:
        scale = (max_value - min_value) / _max_values[pack_type]
        return PackInfo(pack_type, float(scale), float(min_value))

    scale = _get_scale(decimals)
    unique_values = int((max_value - min_value) / scale)
    for p_type, max_val in _max_values.items():
        if unique_values <= max_val:
            return PackInfo(p_type, float(scale), float(min_value))

    raise ValueError("Unable to find appropriate packing")


def pack_to_list(
    data: list | numpy.ndarray,
    pack_info: PackInfo | None = None,
    decimals: int | None = None,
    in_place: bool = True,
):
    """Preform bit packing of input data, utilizing the the pack_info if provided or
    a derived pack_info if not.

    Args:
        data (list | numpy.ndarray): Input data, either in list form
                                        (e.g. list[list[float]] for 2D) or as a numpy array
        pack_info (PackInfo | None, optional): Pre-determined packing info. Defaults to None.
        decimals (int | None, optional): If pack_info is not provided, decimals is used
                                            to derive packing info. Defaults to None.
        in_place (bool, optional): A flag to indicate to preform bit packing in place to the
                                   extent possible. Defaults to True.

    Raises:
        KeyError: If the input data is not of support type.

    Returns:
        PackData: Returns the packed data and meta data (i.e. PackInfo)
    """
    if isinstance(data, numpy.ndarray):
        return pack_numpy_to_list(data, pack_info, decimals)

    if isinstance(data, list):
        return pack_list_to_list(data, pack_info, decimals, in_place)

    raise KeyError(f"Data type ({type(data)}), is not supported")


def pack_numpy_to_numpy(
    data: numpy.ndarray,
    pack_info: PackInfo | None = None,
    decimals: int | None = None,
    in_place: bool = True,
) -> PackData:
    """Preform bit packing of input data, utilizing the the pack_info if provided or
    a derived pack_info if not. Input and output are numpy arrays.

    Args:
        data (numpy.ndarray): Input data.
        pack_info (PackInfo | None, optional): Pre-determined packing info. Defaults to None.
        decimals (int | None, optional): If pack_info is not provided, decimals is used
                                            to derive packing info. Defaults to None.
        in_place (bool, optional): A flag to indicate to preform bit packing in place to the
                                   extent possible. Defaults to True.

    Raises:
        ValueError: If input data is not numpy array

    Returns:
        PackData: Returns the packed data and meta data (i.e. PackInfo), where data will be
                  numpy array.
    """
    if not isinstance(data, numpy.ndarray):
        raise ValueError(f"Data must be a numpy.ndarray but is of type {type(data)}")

    pack_type, scale, offset = _resolve_pack_info(data, pack_info, decimals)

    if in_place:
        if not numpy.issubdtype(data.dtype, numpy.floating):
            raise ValueError("Cannot complete in_place bit packing with non floating point array")
        data -= offset
    else:
        data = data - offset

    data /= scale
    data += 0.5  # for non-negative values adding .5 before truncation is equivalent to round
    return PackData(pack_type, scale, offset, numpy.trunc(data, out=data))


def pack_list_to_list(
    data: list,
    pack_info: PackInfo | None = None,
    decimals: int | None = None,
    in_place: bool = True,
) -> PackData:
    """Preform bit-packing of input data, utilizing the pack_info if provided or
    a derived pack_info if not. Input and output are python list (can be nested lists).

    Args:
        data (list): Input data.
        pack_info (PackInfo | None, optional): Pre-determined packing info. Defaults to None.
        decimals (int | None, optional): If pack_info is not provided, decimals is used
                                            to derive packing info. Defaults to None.
        in_place (bool, optional): A flag to indicate to preform bit packing in place to the
                                   extent possible. Defaults to True.

    Raises:
        ValueError: If input data is not python list

    Returns:
        PackData: Returns the packed data and meta data (i.e. PackInfo), where data will be
                  python list (possibly nested).
    """
    if not isinstance(data, list):
        raise ValueError(f"Data must be a python list but is of type {type(data)}")

    pack_type, scale, offset = _resolve_pack_info(data, pack_info, decimals)
    if in_place:
        return PackData(pack_type, scale, offset, _pack_list_to_list_in_place(data, scale, offset))
    return PackData(pack_type, scale, offset, _pack_list_to_list_copy(data, scale, offset))


def pack_numpy_to_list(
    data: numpy.array,
    pack_info: PackInfo | None = None,
    decimals: int | None = None,
) -> PackData:
    """Preform bit packing of input data, utilizing the the pack_info if provided or
    a derived pack_info if not. Input is numpy array and output is python list.

    Args:
        data (numpy.ndarray): Input data.
        pack_info (PackInfo | None, optional): Pre-determined packing info. Defaults to None.
        decimals (int | None, optional): If pack_info is not provided, decimals is used
                                            to derive packing info. Defaults to None.

    Raises:
        ValueError: If input data is not numpy array

    Returns:
        PackData: Returns the packed data and meta data (i.e. PackInfo), where data will be
                  python list.
    """
    if not isinstance(data, numpy.ndarray):
        raise ValueError(f"Data must be a numpy.ndarray but is of type {type(data)}")

    pack_type, scale, offset = _resolve_pack_info(data, pack_info, decimals)
    return PackData(pack_type, scale, offset, _pack_np_array_to_list(data, scale, offset))


# determine the appropriate pack info, basically if pack info if provided return that,
# else compute it based on decimal, and if nothing else use short packing. This is needed
# because of the overloaded nature of the public pack functions. A caller can provide a
# specific pack_info to use or the decimal precision (which with the actual data can be used to
# create a pack_info), or lastly if not providing a pack_info or decimal then a pack_info using
# short packing would be used.
def _resolve_pack_info(
    data, pack_info: PackInfo | None = None, decimals: int | None = None
) -> PackInfo:
    return (
        PackInfo(pack_info.type, float(pack_info.scale), float(pack_info.offset))
        if pack_info is not None
        else (
            get_pack_info(numpy.min(data), numpy.max(data), decimals=decimals)
            if decimals is not None
            else get_pack_info(numpy.min(data), numpy.max(data), pack_type=PackType.SHORT)
        )
    )


# core packing code specific to in place packing of a list(s)
def _pack_list_to_list_in_place(data: list, scale: float, offset: float) -> list:
    # Convert list into numpy array (it creates a copy)
    np_data = numpy.array(data, dtype=float)
    data = _pack_np_array_to_list(np_data, scale, offset)
    return data


# core packing code specific to packing a list(s) with forced copying
def _pack_list_to_list_copy(data: list, scale: float, offset: float) -> list:
    np_data = numpy.array(data, dtype=float)
    return _pack_np_array_to_list(np_data, scale, offset)


# core packing code specific to packing numpy array to a list, in place not possible
def _pack_np_array_to_list(data: numpy.array, scale: float, offset: float) -> list:
    np_data = numpy.copy(data)
    np_data -= offset
    np_data /= scale
    # for non-negative values, adding 0.5 before truncation is equivalent to rounding
    np_data += 0.5
    # Return the truncated array and a int list.
    return (numpy.trunc(np_data).astype(int)).tolist()


# core packing code using diplib package (sometimes slower than the original so not used but here
# for an option.
# def _diplib_pack(data: numpy.array,
#                 scale: float,
#                 offset: float) -> numpy.array:
#    dip_data = dip.Image(data)
#    dip_data -= offset
#    dip_data /= scale
#    return numpy.trunc(dip_data)


# private lookup for the max value possible for bit packing type
_max_values = {PackType.BYTE: 255, PackType.SHORT: 65535}

_scale_lookup = {0: 1.0, 1: 0.1, 2: 0.01, 3: 0.001, 4: 0.0001, 5: 0.00001, 6: 0.000001}


# private lookup function of num decimal to actual decimals. Using the lookup remove rounding
# issues with math.pow for the most common decimal values
def _get_scale(decimals):
    return _scale_lookup.get(decimals, 0.1**decimals)

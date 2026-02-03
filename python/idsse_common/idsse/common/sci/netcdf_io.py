"""Utilities for reading NetCDF files"""

# ----------------------------------------------------------------------------------
# Created on Mon Feb 13 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Geary J Layne (1)
#     Mackenzie Grimes (2)
#
# ----------------------------------------------------------------------------------

import logging
import os
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

import h5netcdf as h5nc
from dateutil.parser import ParserError, parse as dt_parse
from netCDF4 import Dataset  # pylint: disable=no-name-in-module
from numpy import ndarray

from idsse.common.utils import to_iso

logger = logging.getLogger(__name__)


# cSpell:ignore ncattrs, getncattr, maskandscale
class HasNcAttr(Protocol):
    """Protocol that allows retrieving attributes from a `netCDF4.Dataset` object"""

    def ncattrs(self) -> Sequence[str]:
        """Gives access to list of keys

        Returns:
            Sequence[str]: Keys names for the attributes
        """

    def getncattr(self, key: str) -> any:
        """Gives access to value for specific key

        Args:
            key (str): Name of attribute to be retrieved

        Returns:
            any: The requested attribute, of unknown type
        """


def read_netcdf_global_attrs(filepath: str, use_h5_lib=False) -> dict:
    """Read the global attributes from a Netcdf file

    Args:
        filepath (str): Path to Netcdf file

    Returns:
        dict: Global attributes as dictionary
    """
    if use_h5_lib:
        with h5nc.File(filepath, "r") as nc_file:
            attrs = _attrs_to_dict(nc_file, use_h5_lib=True)
        return attrs

    with Dataset(filepath) as in_file:
        attrs = _attrs_to_dict(in_file)
    return attrs


def read_netcdf(filepath: str, use_h5_lib=False) -> tuple[dict, ndarray]:
    """Reads DAS Netcdf file.

    Args:
        filepath (str): Path to DAS Netcdf file
        use_h5_lib: (bool): if True, python library h5netcdf will be used to do file I/O.
            If False, netCDF4 library will be used. Default is False (netcdf4 will be used).

    Returns:
        tuple[dict, ndarray]: Global attributes and data
    """
    if use_h5_lib:
        with h5nc.File(filepath, "r") as nc_file:
            grid = nc_file.variables["grid"][:]
            attrs = _attrs_to_dict(nc_file, use_h5_lib=True)
            return attrs, grid

    # otherwise, use netcdf4 library (default)
    with Dataset(filepath) as dataset:
        dataset.set_auto_maskandscale(False)
        grid = dataset.variables["grid"][:]

        global_attrs = _attrs_to_dict(dataset)
        return global_attrs, grid


def write_netcdf(attrs: dict, grid: ndarray, filepath: str, use_h5_lib=False) -> str:
    """Store data and attributes to a Netcdf4 file

    Args:
        attrs (dict): Attribute relative to the data to be written
        grid (ndarray): Numpy array of data
        filepath (str): String representation of where to write the file
        use_h5_lib: (bool): if True, python library h5netcdf will be used to do file I/O.
            If False, netCDF4 library will be used. Default is False (netCDF4 will be used).

    Returns:
        str: The location that data was written to
    """
    # ensure parent directories exist
    dirname = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(dirname, exist_ok=True)

    logger.debug("Writing data to: %s", filepath)
    if use_h5_lib:
        with h5nc.File(filepath, "w") as file:
            y_dimensions, x_dimensions = grid.shape
            # set dimensions with a dictionary
            file.dimensions = {"x": x_dimensions, "y": y_dimensions}

            grid_var = file.create_variable("grid", ("y", "x"), "f4")
            grid_var[:] = grid

            for key, value in attrs.items():
                # write datetimes to ISO-8601; h5py.Attributes only understand numpy scalars/strings
                if isinstance(value, datetime):
                    file.attrs[key] = to_iso(value)
                # force non-string attribute to be string (shouldn't be necessary anyway)
                elif not isinstance(value, str):
                    file.attrs[key] = str(value)
                else:
                    file.attrs[key] = value

    # otherwise, write file using netCDF4 library (default)
    with Dataset(filepath, "w", format="NETCDF4") as dataset:
        y_dimensions, x_dimensions = grid.shape
        dataset.createDimension("x", x_dimensions)
        dataset.createDimension("y", y_dimensions)

        grid_var = dataset.createVariable("grid", "f4", ("y", "x"))
        grid_var[:] = grid

        for key, value in attrs.items():
            setattr(dataset, key, str(value))

    return filepath


def _attrs_to_dict(dataset: HasNcAttr | h5nc.File, use_h5_lib=False) -> dict:
    if not use_h5_lib:
        return {key: dataset.getncattr(key) for key in dataset.ncattrs()}

    attrs_dict = {}
    for key, value in dataset.attrs.items():
        # if an attribute is an ISO-8601 string, restore to Python datetime type
        # HACK: no way to detect Attributes datatype from h5netcdf; attempts conversion blindly
        try:
            attrs_dict[key] = dt_parse(value)
        except ParserError:
            attrs_dict[key] = value  # must not have been an ISO-8601 string
    return attrs_dict

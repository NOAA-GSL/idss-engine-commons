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
from typing import Protocol

from netCDF4 import Dataset  # pylint: disable=no-name-in-module
import h5netcdf as h5nc
import numpy as np

logger = logging.getLogger(__name__)


# cSpell:ignore ncattrs, getncattr, maskandscale
class HasNcAttr(Protocol):
    """Protocol that allows retrieving attributes"""
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


def read_netcdf_global_attrs(filepath: str) -> dict:
    """Read the global attributes from a Netcdf file

    Args:
        filepath (str): Path to Netcdf file

    Returns:
        dict: Global attributes as dictionary
    """
    return _read_attrs(Dataset(filepath))


def read_netcdf(filepath: str, use_h5_lib: bool = False) -> tuple[dict, np.ndarray]:
    """Reads DAS Netcdf file.

    Args:
        filepath (str): Path to DAS Netcdf file
        use_h5_lib: (bool): if True, python library h5netcdf will be used to do file I/O.
            If False, netCDF4 library will be used. Default is False (netcdf4 will be used).

    Returns:
        tuple[dict, np.ndarray]: Global attributes and data
    """
    if use_h5_lib:
        with h5nc.File(filepath, 'r') as nc_file:
            grid = nc_file.variables['grid'][:]
            return nc_file.attrs, grid

    # otherwise, use netcdf4 library (default)
    with Dataset(filepath) as dataset:
        dataset.set_auto_maskandscale(False)
        grid = dataset.variables['grid'][:]

        global_attrs = _read_attrs(dataset)
        return global_attrs, grid


def write_netcdf(attrs: dict,
                 grid: np.ndarray,
                 filepath: str,
                 use_h5_lib: bool = False) -> str:
    """Store data and attributes to a Netcdf4 file

    Args:
        attrs (dict): Attribute relative to the data to be written
        grid (np.array): Numpy array of data
        filepath (str): String representation of where to write the file
        use_h5_lib: (bool): if True, python library h5netcdf will be used to do file I/O.
            If False, netCDF4 library will be used. Default is False (netCDF4 will be used).

    Returns:
        str: The location that data was written to
    """
    _make_dirs(filepath)
    logger.debug('Writing data to: %s', filepath)

    if use_h5_lib:
        with h5nc.File(filepath, 'w') as file:
            y_dimensions, x_dimensions = grid.shape
            # set dimensions with a dictionary
            file.dimensions = {'x': x_dimensions, 'y': y_dimensions}

            grid_var = file.create_variable('grid', ('y', 'x'), 'f4')
            grid_var[:] = grid

            for key, value in attrs.items():
                file.attrs[key] = value

    else:
        # otherwise, write file using netCDF4 library (default)
        with Dataset(filepath, 'w', format='NETCDF4') as dataset:
            y_dimensions, x_dimensions = grid.shape
            dataset.createDimension('x', x_dimensions)
            dataset.createDimension('y', y_dimensions)

            grid_var = dataset.createVariable('grid', 'f4', ('y', 'x'))
            grid_var[:] = grid

            for key, value in attrs.items():
                setattr(dataset, key, str(value))

    return filepath


def _make_dirs(filename: str):
    dirname = os.path.dirname(os.path.abspath(filename))
    os.makedirs(dirname, exist_ok=True)


def _read_attrs(has_nc_attr: HasNcAttr) -> dict:
    return {key: has_nc_attr.getncattr(key) for key in has_nc_attr.ncattrs()}

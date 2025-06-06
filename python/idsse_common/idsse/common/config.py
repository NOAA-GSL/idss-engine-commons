"""Utility for loading configuration data"""

# ------------------------------------------------------------------------------
# Created on Wed Mar 01 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# -------------------------------------------------------------------------------

import glob
import json
import logging
from collections.abc import Iterable
from inspect import signature
from typing import Self

logger = logging.getLogger(__name__)


class Config:
    """Configuration data class"""

    def __init__(
        self,
        config: dict | Iterable[dict] | str,
        keys: Iterable | str | None = None,
        recursive: bool = False,
        ignore_missing: bool = False,
    ) -> None:

        self._previous = None
        self._next = None

        # if keys is None, indicating default key (class name) should be used
        if keys is None:
            keys = self.__class__.__name__
        # check if keys is empty, set to empty list, results in not looking for sub structs
        elif isinstance(keys, str) and keys == "":
            keys = []

        # check is config is a string representation of a dictionary
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                logger.debug("Unsuccessful loading config as string rep of dict")

        # if config is a string use it to find filepaths
        if isinstance(config, str):
            filepaths = glob.glob(config, recursive=recursive)
            if len(filepaths) == 0:
                raise FileNotFoundError
            self._from_filepaths(filepaths, keys)
        # since it is not a string, assuming it is a dictionary or list of dictionaries
        else:
            if isinstance(config, list):
                self._from_config_dicts(config, keys)
            else:
                self._from_config_dict(config, keys)

        # check for all expected config attributes
        if not ignore_missing:
            for key, value in self.__dict__.items():
                if value is None and key not in ["_next", "_previous"]:
                    raise NameError(f"name ({key}) not found in config")

    @property
    def first(self) -> Self:
        """Get the first configuration"""
        if self._previous is None:
            return self
        return self._previous.first

    @property
    def next(self) -> Self:
        """Move to the next configuration"""
        return self._next

    @property
    def previous(self) -> Self:
        """Move to the previous configuration"""
        return self._previous

    @property
    def last(self) -> Self:
        """Get the last configuration"""
        if self._next is None:
            return self
        return self._next.last

    def _load_from_filepath(self, filepath: str) -> dict:
        with open(filepath, "r", encoding="utf8") as file:
            return json.load(file)

    def _from_filepaths(self, filepaths: Iterable[str], keys: str) -> Self:
        config_dicts = [self._load_from_filepath(filepath) for filepath in filepaths]
        self._from_config_dicts(config_dicts, keys)

    def _from_config_dict(self, config_dict: dict, keys: str) -> Self:
        if keys is not None:
            if isinstance(keys, str):
                config_dict = config_dict[keys]
            else:
                for key in keys:
                    config_dict = config_dict[key]

        # update the instance dictionary to hold all configuration attributes
        return self.__dict__.update(config_dict)

    def _from_config_dicts(self, config_dicts: Iterable[dict], keys: str) -> Self:
        self._from_config_dict(config_dicts[0], keys)
        for config_dict in config_dicts[1:]:
            # if inherited class takes only one argument
            if len(signature(type(self)).parameters) == 1:
                self._next = self.__class__(config_dict)
            else:
                self._next = self.__class__(config_dict, keys=keys)
            self._next._previous = self  # pylint: disable=protected-access

        return self

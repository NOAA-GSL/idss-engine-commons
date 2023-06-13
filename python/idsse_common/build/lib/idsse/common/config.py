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
from inspect import signature
from typing import Self, Union

logger = logging.getLogger(__name__)


class Config:
    """Configuration data class"""

    def __init__(self,
                 config: Union[dict, str],
                 keys: Union[list, str] = None,
                 recursive: bool = False,
                 ignore_missing: bool = False) -> None:

        self._previous = None
        self._next = None

        # if keys is None, indicating default key (class name) should be used
        if keys is None:
            keys = self.__class__.__name__
        # check if keys is empty, set to empty list, results in not looking for sub structs
        elif isinstance(keys, str) and keys == '':
            keys = []

        # check is config is a string representation of a dictionary
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.debug('Unsuccessful loading config as string rep of dict')

        # if config is a string use it to find filepaths
        if isinstance(config, str):
            filepaths = glob.glob(config, recursive=recursive)
            if len(filepaths) == 0:
                raise FileNotFoundError
            elif len(filepaths) == 1:
                self._from_filepath(filepaths[0], keys)
            else:
                self._from_filepaths(filepaths, keys)
        # since it is not a string, assuming it is a dictionary or list of dictionaries
        else:
            if isinstance(config, list):
                self._from_config_dicts(config, keys)
            else:
                self._from_config_dict(config, keys)

        # check for all expected config attributes
        if not ignore_missing:
            for k, v in self.__dict__.items():
                if v is None and k not in ['_next', '_previous']:
                    raise NameError(f'name ({k}) not found in config')

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

    def _load_from_filepath(self, filepath) -> dict:
        with open(filepath, 'r', encoding='utf8') as file:
            return json.load(file)

    def _from_filepath(self, filepath, keys) -> Self:
        config_dicts = self._load_from_filepath(filepath)
        if isinstance(config_dicts, list):
            self._from_config_dicts(config_dicts, keys)
        else:
            self._from_config_dict(config_dicts, keys)

    def _from_filepaths(self, filepaths, keys) -> Self:
        config_dicts = [self._load_from_filepath(filepath)
                        for filepath in filepaths]
        self._from_config_dicts(config_dicts, keys)

    def _from_config_dict(self, config_dict: dict, keys: str) -> Self:
        if keys is not None:
            if isinstance(keys, str):
                config_dict = config_dict[keys]
            else:
                for key in keys:
                    config_dict = config_dict[key]
        # update the instance dictionary to hold all configuration attributes
        self.__dict__.update(config_dict)

    def _from_config_dicts(self, config_dicts, keys: str) -> Self:
        self._from_config_dict(config_dicts[0], keys)
        for config_dict in config_dicts[1:]:
            # if inherited class takes only one argument
            if len(signature(type(self)).parameters) == 1:
                self._next = type(self)(config_dict)
            else:
                self._next = type(self)(config_dict, keys)
            self._next._previous = self  # pylint: disable=protected-access


def _example():
    class NameAsKeyConfig(Config):
        """Testing config class the uses class name as key"""
        def __init__(self, config: Union[dict, str]) -> None:
            """To create a config that uses it's class name when look for nested config,
            pass None to the super.__init()"""
            self.idiom = None
            self.metaphor = None
            super().__init__(config, None)

    class WithoutKeyConfig(Config):
        """Testing config class the uses no key"""
        def __init__(self, config: Union[dict, str]) -> None:
            """To create a config that does NOT look for config nested under a key,
            pass an empty string to the super.__init()"""
            self.idiom = None
            self.metaphor = None
            super().__init__(config, '')

    class RequiresKeyConfig(Config):
        """Testing config class that requires key to be provided"""
        def __init__(self, config: Union[dict, str], key: Union[list, str]) -> None:
            """To create a config that requires a user provided name when look for nested config,
            pass a key as string or list of string to the super.__init()"""
            self.idiom = None
            self.metaphor = None
            super().__init__(config, key)

    def get_config_dict(key: Union[list, str]) -> dict:
        idioms = ['Out of hand',
                  'See eye to eye',
                  'Under the weather',
                  'Cut the mustard']
        metaphors = ['blanket of stars',
                     'weighing on my mind',
                     'were a glaring light',
                     'floated down the river']
        if key is None:
            return {'idiom': random.choice(idioms),
                    'metaphor': random.choice(metaphors)}
        if isinstance(key, str):
            key = [key]
        config_dict = {'idiom': random.choice(idioms),
                       'metaphor': random.choice(metaphors)}
        for k in reversed(key):
            config_dict = {k: config_dict}
        return config_dict

    # example of config that uses class name to identify relevant block of data
    config_dict = get_config_dict('NameAsKeyConfig')
    logging.info(config_dict)
    config = NameAsKeyConfig(config_dict)
    logging.info('Idiom:', config.idiom)
    logging.info('Metaphor:', config.metaphor)

    # example of config with block of data at top level
    config_dict = get_config_dict(None)
    logging.info(config_dict)
    config = WithoutKeyConfig(config_dict)
    logging.info('Idiom:', config.idiom)
    logging.info('Metaphor:', config.metaphor)

    # example of config with relevant block of data nested
    config_dict = get_config_dict('NestKey')
    logging.info(config_dict)
    config = RequiresKeyConfig(config_dict, 'NestKey')
    logging.info('Idiom:', config.idiom)
    logging.info('Metaphor:', config.metaphor)


if __name__ == '__main__':
    import random

    _example()

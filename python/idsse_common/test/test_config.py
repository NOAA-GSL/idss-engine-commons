"""Test suit for config.py"""
# --------------------------------------------------------------------------------
# Created on Fri Mar 17 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary J Layne
#
# --------------------------------------------------------------------------------
import json
import pytest

from idsse.common.config import Config


# pylint: disable=missing-function-docstring

def test_load_from_dict_without_key():
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.a_key = None
            super().__init__(config, '')

    config = WithoutKeyConfig({'a_key': 'value found'})
    assert config.a_key == 'value found'


def test_load_from_dict_as_string_without_key():
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.some_key = None
            super().__init__(config, '')

    config = WithoutKeyConfig('{"some_key": "value found"}')
    assert config.some_key == 'value found'


def test_load_from_dict_with_name_key():
    class NameAsKeyConfig(Config):
        """Config class that class name as the key to find config data"""
        def __init__(self, config: dict) -> None:
            self.best_key = None
            super().__init__(config, None)

    config = NameAsKeyConfig({'NameAsKeyConfig': {'best_key': 'value found'}})
    assert config.best_key == 'value found'


def test_load_from_dict_require_string_key():
    class RequireKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict, key: str) -> None:
            self.some_key = None
            super().__init__(config, key)

    config = RequireKeyConfig('{"custom_key": {"some_key": "value found"}}', 'custom_key')
    assert config.some_key == 'value found'


def test_load_from_dict_require_list_key():
    class RequireKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict, key: list) -> None:
            self.some_key = None
            super().__init__(config, key)

    key_list = ['custom_key', 'custom_key2']
    config = RequireKeyConfig('{"custom_key": {"custom_key2": {"some_key": "value found"}}}',
                              key_list)
    assert config.some_key == 'value found'


def test_load_with_missing_attribute_should_fail():
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.a_key = None
            super().__init__(config, '')

    with pytest.raises(NameError):
        WithoutKeyConfig({'diff_key': 'value found'})


def test_load_with_ignore_missing_attribute():
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.a_key = None
            self.b_key = None
            super().__init__(config, '', ignore_missing=True)

    config = WithoutKeyConfig({'a_key': 'value for a'})
    assert config.a_key == 'value for a'


def test_load_from_file(mocker):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.y_this_is_a_key = None
            super().__init__(config, '')

    mocker.patch('glob.glob', return_value=['filename'])

    read_data = json.dumps({"y_this_is_a_key": "value found in file"})
    mocker.patch('builtins.open', mocker.mock_open(read_data=read_data))

    config = WithoutKeyConfig('path/to/file')

    assert config.y_this_is_a_key == "value found in file"


def test_load_from_files_with_out_key(mocker):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.y_this_is_a_key = None
            super().__init__(config, [])

    mocker.patch('glob.glob', return_value=['filename1', 'filename2'])

    read_data = [json.dumps({"y_this_is_a_key": "value found in file1"}),
                 json.dumps({"y_this_is_a_key": "value found in file2"})]
    mock_files = mocker.patch('builtins.open', mocker.mock_open(read_data=read_data[0]))
    mock_files.side_effect = (mocker.mock_open(read_data=data).return_value for data in read_data)

    config = WithoutKeyConfig('path/to/dir')

    assert config.y_this_is_a_key == "value found in file1"
    assert config.next.y_this_is_a_key == "value found in file2"


def test_load_from_files_with_key(mocker):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""
        def __init__(self, config: dict) -> None:
            self.y_this_is_a_key = None
            super().__init__(config, 'config_key')

    mocker.patch('glob.glob', return_value=['filename1', 'filename2'])

    read_data = [json.dumps({"config_key": {"y_this_is_a_key": "value found in file1"}}),
                 json.dumps({"config_key": {"y_this_is_a_key": "value found in file2"}})]
    mock_files = mocker.patch('builtins.open', mocker.mock_open(read_data=read_data[0]))
    mock_files.side_effect = (mocker.mock_open(read_data=data).return_value for data in read_data)

    config = WithoutKeyConfig('path/to/dir')

    assert config.y_this_is_a_key == "value found in file1"
    assert config.next.y_this_is_a_key == "value found in file2"

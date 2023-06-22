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
from pytest import MonkeyPatch
from unittest.mock import Mock, mock_open

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

    config = RequireKeyConfig(
        '{"custom_key": {"some_key": "value found"}}', 'custom_key')
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


def test_config_str_with_no_files_raises_error(monkeypatch: MonkeyPatch):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""

        def __init__(self, config: str) -> None:
            self.a_key = None
            super().__init__(config, '')

    monkeypatch.setattr('glob.glob', Mock(return_value=[]))

    with pytest.raises(FileNotFoundError):
        WithoutKeyConfig('wont_be_found')


def test_config_list_of_dicts_succeeds():
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""

        def __init__(self, config: dict) -> None:
            self.a_key = None
            self.b_key = None
            super().__init__(config, '', ignore_missing=True)

    config = WithoutKeyConfig(
        [{'a_key': 'value for a'}, {'b_key': 'value for b'}])
    
    assert config.a_key == 'value for a'
    assert config.next.b_key == 'value for b'


def test_load_with_ignore_missing_attribute():
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""

        def __init__(self, config: dict) -> None:
            self.a_key = None
            self.b_key = None
            super().__init__(config, '', ignore_missing=True)

    config = WithoutKeyConfig({'a_key': 'value for a'})
    assert config.a_key == 'value for a'


def test_load_from_file(monkeypatch: MonkeyPatch):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""

        def __init__(self, config: dict) -> None:
            self.y_this_is_a_key = None
            super().__init__(config, '')

    monkeypatch.setattr('glob.glob', Mock(return_value=['filename']))

    read_data = json.dumps({"y_this_is_a_key": "value found in file"})
    monkeypatch.setattr('builtins.open', mock_open(read_data=read_data))

    config = WithoutKeyConfig('path/to/file')

    assert config.y_this_is_a_key == "value found in file"


def test_load_from_files_with_out_key(monkeypatch: MonkeyPatch):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""

        def __init__(self, config: dict) -> None:
            self.y_this_is_a_key = None
            super().__init__(config, [])

    monkeypatch.setattr('glob.glob', Mock(
        return_value=['filename1', 'filename2']))

    read_data = [json.dumps({"y_this_is_a_key": "value found in file1"}),
                 json.dumps({"y_this_is_a_key": "value found in file2"})]
    mock_files = Mock(side_effect=(
        mock_open(read_data=data).return_value for data in read_data))
    monkeypatch.setattr('builtins.open', mock_files)

    config = WithoutKeyConfig('path/to/dir')

    assert config.y_this_is_a_key == "value found in file1"
    assert config.next.y_this_is_a_key == "value found in file2"
    assert mock_files.call_count == 2


def test_load_from_files_with_key(monkeypatch: MonkeyPatch):
    class WithoutKeyConfig(Config):
        """Config class that doesn't use a key to find config data"""

        def __init__(self, config: dict) -> None:
            self.y_this_is_a_key = None
            super().__init__(config, 'config_key')

    monkeypatch.setattr('glob.glob', Mock(
        return_value=['filename1', 'filename2']))

    read_data = [json.dumps({"config_key": {"y_this_is_a_key": "value found in file1"}}),
                 json.dumps({"config_key": {"y_this_is_a_key": "value found in file2"}})]
    mock_files = Mock(side_effect=(
        mock_open(read_data=data).return_value for data in read_data))
    monkeypatch.setattr('builtins.open', mock_files)

    config = WithoutKeyConfig('path/to/dir')

    assert config.y_this_is_a_key == "value found in file1"
    assert config.next.y_this_is_a_key == "value found in file2"
    assert mock_files.call_count == 2

'''Test suite for DAS web message using validate_schema.py'''
# ----------------------------------------------------------------------------------
# Created on Mon Nov 20 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name
# pylint: disable=no-name-in-module,duplicate-code
# cspell:ignore geodist

from jsonschema import Validator
from jsonschema.exceptions import ValidationError
from pytest import fixture, raises

from idsse.common.validate_schema import get_validator


@fixture
def das_web_request_validator() -> Validator:
    schema_name = 'das_web_request_schema'
    return get_validator(schema_name)


@fixture
def das_web_response_validator() -> Validator:
    schema_name = 'das_web_response_schema'
    return get_validator(schema_name)


@fixture
def das_web_request_message() -> dict:
    return {
        'issueDt': '2023-01-10T08:00:00.000Z',
        'dataRequest': 'A AND B',
        'parts': [
            {
                'name': 'A',
                'duration': 0,
                'arealPercentage': 0,
                'product': 'NBM',
                'field': 'WINDSPEED',
                'units': 'MilesPerHour',
                'region': 'CO',
                'relational': 'GREATER THAN',
                'thresh': 5,
                'mapping': {
                    'min': 0.0,
                    'max': 20.0,
                    'clip': 'true'
                }
            },
            {
                'name': 'B',
                'duration': 0,
                'arealPercentage': 0,
                'product': 'NBM',
                'field': 'TEMPERATURE',
                'units': 'Fahrenheit',
                'region': 'CO',
                'relational': 'LESS THAN OR EQUAL',
                'thresh': 30,
                'mapping': {
                    'min': 15.0,
                    'max': 45.0,
                    'clip': 'true'
                }
            }
        ],
        'valids': [
            '2023-01-11T06:00:00.000Z',
            '2023-01-11T07:00:00.000Z',
            '2023-01-11T08:00:00.000Z',
            '2023-01-11T09:00:00.000Z',
            '2023-01-11T10:00:00.000Z',
            '2023-01-11T11:00:00.000Z',
            '2023-01-11T12:00:00.000Z',
            '2023-01-11T13:00:00.000Z',
            '2023-01-11T14:00:00.000Z',
            '2023-01-11T15:00:00.000Z',
            '2023-01-11T16:00:00.000Z',
            '2023-01-11T17:00:00.000Z',
            '2023-01-11T18:00:00.000Z'
        ],
        'bbox': {
            'botLeft': [910, 829],
            'topRight': [1010, 929]
        }
    }


@fixture
def das_web_response_message() -> dict:
    return {
        'issueDt': '2023-01-10T08:00:00.000Z',
        'dataRequest': 'A',
        'parts': [
            {
                'name': 'A',
                'duration': 0,
                'arealPercentage': 0,
                'product': 'NBM',
                'field': 'WINDSPEED',
                'units': 'MilesPerHour',
                'region': 'CO',
                'relational': 'GREATER THAN',
                'thresh': 5,
                'mapping': {
                    'min': 0.0,
                    'max': 20.0,
                    'clip': 'true'
                }
            }
        ],
        'valids': [
            '2023-01-11T06:00:00.000Z',
            '2023-01-11T18:00:00.000Z'
        ],
        'bbox': {
            'botLeft': [100, 102],
            'topRight': [200, 202]
        },
        'data': {
            '2023-01-11T06:00:00.000Z': [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ],
            '2023-01-11T18:00:00.000Z': [
                [9, 8, 7],
                [6, 5, 4],
                [3, 2, 1]
            ],
            'scale': 10
        }
    }


def test_validate_das_web_request_message(das_web_request_validator: Validator,
                                          das_web_request_message: dict):
    try:
        das_web_request_validator.validate(das_web_request_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_web_request_message_with_bbox_list(das_web_request_validator: Validator,
                                                         das_web_request_message: dict):
    bbox = das_web_request_message.pop('bbox')
    das_web_request_message['bbox'] = [bbox['botLeft'], bbox['topRight']]
    try:
        das_web_request_validator.validate(das_web_request_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_web_request_message_bad_bbox_list(das_web_request_validator: Validator,
                                                        das_web_request_message: dict):
    bbox = das_web_request_message.pop('bbox')
    bot_left = bbox['botLeft']
    top_right = bbox['topRight']
    # move one value from bottom  and adding to top, making neither represent a coordinate
    top_right.append(bot_left.pop(1))
    das_web_request_message['bbox'] = [bot_left, top_right]
    with raises(ValidationError):
        das_web_request_validator.validate(das_web_request_message)


def test_validate_das_web_request_message_bad_bbox_obj(das_web_request_validator: Validator,
                                                       das_web_request_message: dict):
    # replace the bottom left int coordinate with a float
    das_web_request_message['bbox']['botLeft'][0] = 1.2
    with raises(ValidationError):
        das_web_request_validator.validate(das_web_request_message)


def test_validate_das_web_request_message_multi_product(das_web_request_validator: Validator,
                                                        das_web_request_message: dict):
    # replace the single product with multiple product structure (like in criteria and eventPort)
    das_web_request_message['parts'][0]['product'] = {
        'fcst': [
            'NBM'
        ]
    }
    with raises(ValidationError):
        das_web_request_validator.validate(das_web_request_message)


def test_validate_das_web_response_message(das_web_response_validator: Validator,
                                           das_web_response_message: dict):
    try:
        das_web_response_validator.validate(das_web_response_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_web_response_message_without_data(das_web_response_validator: Validator,
                                                        das_web_response_message: dict):
    # remove data
    das_web_response_message.pop('data')
    with raises(ValidationError):
        das_web_response_validator.validate(das_web_response_message)


def test_validate_das_web_response_message_bad_data_key(das_web_response_validator: Validator,
                                                        das_web_response_message: dict):
    # add to data a key that is not scale, offset, datetime
    das_web_response_message['data']['not scale/offset or datetime'] = 3
    with raises(ValidationError):
        das_web_response_validator.validate(das_web_response_message)


def test_validate_das_web_response_message_bad_data(das_web_response_validator: Validator,
                                                    das_web_response_message: dict):
    # add to data a key that is not scale, offset, datetime
    validDt = das_web_response_message['valids'][0]
    das_web_response_message['data'][validDt] = [['strings'], ['not', 'numbers']]
    with raises(ValidationError):
        das_web_response_validator.validate(das_web_response_message)

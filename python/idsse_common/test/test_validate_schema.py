'''Test suite for validate_schema.py'''
# ----------------------------------------------------------------------------------
# Created on Fri Aug 04 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------

from jsonschema.exceptions import ValidationError
import pytest

from idsse.common.validate_schema import get_validator

# pylint: disable=missing-function-docstring, line-too-long


def test_validate_das_valid_request():
    message = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}

    schema_name = 'das_available_data_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_data_request():
    message = {
        'sourceType': 'data',
        'sourceObj': {
            'product': 'NBM',
            'region': 'CO',
            'field': 'WINDSPEED',
            'valid': '2022-11-12T00:00:00.000Z',
            'issue': '2022-11-11T14:00:00.000Z'
        }
    }

    schema_name = 'das_data_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_unit_request():
    message = {
        'sourceType': 'units',
        'sourceObj': {
            'units': 'F',
            'source': {
                'sourceType': 'data',
                'sourceObj': {
                    'product': 'NBM.AWS.GRIB',
                    'region': 'CO',
                    'issue': '2022-01-02T12:00:00.000Z',
                    'valid': '2022-01-02T15:00:00.000Z',
                    'field': 'TEMP'
                }
            }
        }
    }
    schema_name = 'das_request_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_criteria_request():
    message = {
        "sourceType": "condition",
        "sourceObj": {
            "mapping": {"endWeight": [0, 1, 0],
                        "startWeight": [0, 1, 0],
                        "controlPoints": ["-Inf", 35, 75, 100]},
            "relational": "LESSTHAN",
            "source": {
                "sourceType": "units",
                "sourceObj": {
                    "units": "F",
                    "source": {
                        "sourceType": "data",
                        "sourceObj": {
                            "product": "NBM",
                            "region": "CO",
                            "field": "TEMP",
                            "valid": "2022-11-12T00:00:00.000Z",
                            "issue": "2022-11-11T14:00:00.000Z"}}}},
            "thresh": 60}}

    schema_name = 'das_request_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_criteria_join_request():
    message = {
        "sourceType": "conditionJoin",
        "sourceObj": {
            "sources": [{
                "sourceType": "condition",
                "sourceObj": {
                    "mapping": {
                        "endWeight": [0, 1, 0],
                        "startWeight": [0, 1, 0],
                        "controlPoints": ["-Infinity", 35, 75, "Infinity"]},
                    "relational": "LESSTHAN",
                    "source": {
                        "sourceType": "units",
                        "sourceObj": {
                            "units": "F",
                            "source": {
                                "sourceType": "data",
                                "sourceObj": {
                                    "product": "NBM",
                                    "field": "TEMP",
                                    "region": "CO",
                                    "valid": "2022-11-12T00:00:00.000Z",
                                    "issue": "2022-11-11T14:00:00.000Z"}}},
                        "label": "NBM:TEMP:Fahrenheit"},
                    "thresh": 60},
                "label": "NBM:TEMP:Fahrenheit:LT:60.000:35.000:75.000:true"},
                {
                "sourceType": "condition",
                "sourceObj": {
                    "mapping": {
                        "endWeight": [0, 1, 0],
                        "startWeight":[0, 1, 0],
                        "controlPoints": ["-Infinity", 0, 5, "Infinity"]},
                    "relational": "GREATERTHAN",
                    "source": {
                        "sourceType": "units",
                        "sourceObj": {
                            "units": "MPH",
                            "source": {
                                "sourceType": "data",
                                "sourceObj": {
                                    "product": "NBM",
                                    "field": "WINDSPEED",
                                    "region": "CO",
                                    "valid": "2022-11-12T00:00:00.000Z",
                                    "issue": "2022-11-11T14:00:00.000Z"}}},
                        "label": "NBM:WINDSPEED:MilesPerHour"},
                    "thresh": 3},
                "label": "NBM:WINDSPEED:MilesPerHour:GT:3.000:0.000:5.000:true"}],
            "join": "AND"},
        "label": "AND(NBM:TEMP:Fahrenheit:LT:60.000:35.000:75.000:true, NBM:WINDSPEED:MilesPerHour:GT:3.000:0.000:5.000:true)"}  # noqa: E501

    schema_name = 'das_request_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_good_criteria_message():
    message = {'corrId': {'originator': 'IDSSe',
                          'issueDt': '_',
                          'uuid': 'dc7ad8c1-5ff2-416f-9fee-66c598256189'},
               'issueDt': '2018-11-13T20:20:39+00:00',
               'validDt': {'start': '2018-11-13T21:20:39+00:00',
                           'end': '2018-11-13T23:20:39+00:00'},
               'tags': {'values': ['bob', 'uncle'], 'keyValues': {}},
               'location': {'features': [{'type': 'Feature',
                                          'properties': {'innerRadius': 3,
                                                         'outerRadius': 4},
                                          'geometry': {
                                              'type': 'Point',
                                              'coordinates': [
                                                  -105.10392834544123,
                                                  40.16676831094053]}}],
                            'buffer': 1,
                            'bufferUnits': 'miles'}}

    schema_name = 'criteria_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_bad_criteria_message():
    message = {}

    schema_name = 'criteria_schema'
    validator = get_validator(schema_name)

    with pytest.raises(ValidationError):
        validator.validate(message)


def test_validate_good_new_data_message():
    message = {'product': 'NBM',
               'region': 'AK',
               'issue': '2023-2-11T14:00:00.000Z',
               'valid': '2023-2-11T20:00:00.000Z',
               'field': ['TEMP', 'WINDSPEED']}

    schema_name = 'new_data_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'

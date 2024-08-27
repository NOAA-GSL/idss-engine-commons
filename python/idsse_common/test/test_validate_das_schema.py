'''Test suite for DAS messages using validate_schema.py'''
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
# pylint: disable=duplicate-code
# cspell:ignore geodist

from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator
from pytest import fixture, raises

from idsse.common.validate_schema import get_validator


@fixture
def das_info_request() -> Validator:
    schema_name = 'das_info_request_schema'
    return get_validator(schema_name)


@fixture
def data_request_validator() -> Validator:
    schema_name = 'das_data_request_schema'
    return get_validator(schema_name)


@fixture
def data_response_validator() -> Validator:
    schema_name = 'das_data_response_schema'
    return get_validator(schema_name)


@fixture
def das_data_message() -> dict:
    return {
        'sourceType': 'join',
        'sourceObj': {
            'sources': [{
                'sourceType': 'condition',
                'sourceObj': {
                    'mapping': {
                        'endWeight': [0, 1, 0],
                        'startWeight': [0, 1, 0],
                        'controlPoints': ['-Infinity', 35, 75, 'Infinity']},
                    'relational': 'LESSTHAN',
                    'source': {
                        'sourceType': 'units',
                        'sourceObj': {
                            'units': 'F',
                            'source': {
                                'sourceType': 'data',
                                'sourceObj': {
                                    'product': 'NBM',
                                    'field': 'TEMP',
                                    'region': 'CONUS',
                                    'valid': '2022-11-12T00:00:00.000Z',
                                    'issue': '2022-11-11T14:00:00.000Z'}}},
                        'label': 'NBM:TEMP:Fahrenheit'},
                    'thresh': 60},
                'label': 'NBM:TEMP:Fahrenheit:LT:60.000:35.000:75.000:true'},
                {
                'sourceType': 'condition',
                'sourceObj': {
                    'mapping': {
                        'endWeight': [0, 1, 0],
                        'startWeight': [0, 1, 0],
                        'controlPoints': ['-Infinity', 0, 5, 'Infinity']},
                    'relational': 'GREATERTHAN',
                    'source': {
                        'sourceType': 'units',
                        'sourceObj': {
                            'units': 'MPH',
                            'source': {
                                'sourceType': 'data',
                                'sourceObj': {
                                    'product': 'NBM',
                                    'field': 'WINDSPEED',
                                    'region': 'CONUS',
                                    'valid': '2022-11-12T00:00:00.000Z',
                                    'issue': '2022-11-11T14:00:00.000Z'}}},
                        'label': 'NBM:WINDSPEED:MilesPerHour'},
                    'thresh': 3},
                'label': 'NBM:WINDSPEED:MilesPerHour:GT:3.000:0.000:5.000:true'}],
            'join': 'AND'},
        'label': ('AND(NBM:TEMP:Fahrenheit:LT:60.000:35.000:75.000:true, '
                  'NBM:WINDSPEED:MilesPerHour:GT:3.000:0.000:5.000:true)')
    }


# tests
def test_validate_das_issue_request(das_info_request: Validator):
    message = {'sourceType': 'issue',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PUERTO_RICO',
                             'field': 'TEMP',
                             }}
    try:
        das_info_request.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_issue_request(das_info_request: Validator):
    # message is missing 'region'
    message = {'sourceType': 'field',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'field': 'TEMP',
                             'valid': '2022-01-02T15:00:00.000Z'
                             }}
    with raises(ValidationError):
        das_info_request.validate(message)


def test_validate_das_valid_request(das_info_request: Validator):
    message = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PUERTO_RICO',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    try:
        das_info_request.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_valid_request(das_info_request: Validator):
    # message is missing 'field'
    message = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PUERTO_RICO',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    with raises(ValidationError):
        das_info_request.validate(message)


def test_validate_das_lead_request(das_info_request: Validator):
    message = {'sourceType': 'lead',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PUERTO_RICO',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    try:
        das_info_request.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_lead_request(das_info_request: Validator):
    # message is missing 'product'
    message = {'sourceType': 'valid',
               'sourceObj': {'region': 'PUERTO_RICO',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    with raises(ValidationError):
        das_info_request.validate(message)


def test_validate_das_field_request(das_info_request: Validator):
    message = {'sourceType': 'field',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PUERTO_RICO',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z',
                             'valid': '2022-01-02T15:00:00.000Z'
                             }}
    try:
        das_info_request.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_field_request(das_info_request: Validator):
    # message is missing 'issue'
    message = {'sourceType': 'field',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PUERTO_RICO',
                             'field': 'TEMP',
                             'valid': '2022-01-02T15:00:00.000Z'
                             }}
    with raises(ValidationError):
        das_info_request.validate(message)


def test_validate_das_data_request(data_request_validator: Validator):
    message = {
        'sourceType': 'data',
        'sourceObj': {
            'product': 'NBM',
            'region': 'CONUS',
            'field': 'WINDSPEED',
            'valid': '2022-11-12T00:00:00.000Z',
            'issue': '2022-11-11T14:00:00.000Z'
        }
    }
    try:
        data_request_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_data_request(data_request_validator: Validator):
    # missing product
    message = {
        'sourceType': 'data',
        'sourceObj': {
            'region': 'CONUS',
            'field': 'WINDSPEED',
            'valid': '2022-11-12T00:00:00.000Z',
            'issue': '2022-11-11T14:00:00.000Z'
        }
    }
    with raises(ValidationError):
        data_request_validator.validate(message)


def test_validate_das_opr_with_single_source_request(data_request_validator: Validator):
    # this is an example of a unit conversion operator, the operator itself is not be validated
    message = {
        'sourceType': 'units',
        'sourceObj': {
            'units': 'F',
            'source': {
                'sourceType': 'data',
                'sourceObj': {
                    'product': 'NBM.AWS.GRIB',
                    'region': 'CONUS',
                    'issue': '2022-01-02T12:00:00.000Z',
                    'valid': '2022-01-02T15:00:00.000Z',
                    'field': 'TEMP'
                }
            }
        }
    }
    try:
        data_request_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_opr_with_single_source_request(data_request_validator: Validator):
    # this is an example of a unit conversion operator, the operator itself is not validated
    message = {
        'sourceType': 'units',
        'sourceObj': {
            'units': 'F',
            'source': {
                'sourceType': 'field',
                'sourceObj': {
                    'product': 'NBM.AWS.GRIB',
                    'region': 'CONUS',
                    'issue': '2022-01-02T12:00:00.000Z',
                    'valid': '2022-01-02T15:00:00.000Z',
                    'field': 'TEMP'
                }
            }
        }
    }
    with raises(ValidationError):
        data_request_validator.validate(message)


def test_validate_das_opr_with_multi_sources_request(data_request_validator: Validator,
                                                     das_data_message: dict):
    # this is an example of a logical join operator, the operator itself is not validated
    try:
        data_request_validator.validate(das_data_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_opr_with_multi_sources_request(data_request_validator: Validator,
                                                         das_data_message: dict):
    # one of the operator object does not contains 'source', has 'not_source' instead
    mapping_opr = das_data_message['sourceObj']['sources'][1]['sourceObj']
    mapping_opr['not_source'] = mapping_opr.pop('source')
    with raises(ValidationError):
        data_request_validator.validate(das_data_message)


def test_validate_das_data_response(data_response_validator: Validator):
    message = {
        "corrId": {
            "issueDt": "2023-01-10T08:00:00Z",
            "originator": "IDSSe",
            "uuid": "53430eaa-1db4-4095-bf13-a26e45223d9a"
        },
        "request": {
            'sourceType': 'data',
            'sourceObj': {
                'product': 'NBM',
                'region': 'CONUS',
                'field': 'TEMP',
                'valid': '2022-11-12T00:00:00.000Z',
                'issue': '2022-11-11T14:00:00.000Z'
            }
        },
        "data_requested": {
            "filenames": {
                "Deterministic":
                "/data/share/2023/01/10/NBM.AWS.GRIB/Criteria/Criteria/gridstore-1309066818.nc"
            },
            "issue_dt": "2023-01-10T08:00:00Z",
            "valid_dt": "2023-01-11T06:00:00Z",
            "proj_name": "NBM",
            "proj_spec": "+proj=lcc +lat_0=25.0 +lon_0=-95.0 +lat_1=25.0 +a=6371200",
            "grid_spec": ("+dx=2539.703 +dy=2539.703 +w=100 +h=100 "
                          "+lat_ll=41.05894633497196 +lon_ll=-106.02046021316575"),
            "data_prod": "NBM",
            "data_name": "TEMP",
            "data_loc": "",
            "units": "Fahrenheit",
            "region": "CONUS",
            "slice": "slice"
        }
    }

    try:
        data_response_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'

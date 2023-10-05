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
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,no-name-in-module

from jsonschema import Validator
from jsonschema.exceptions import ValidationError
from pytest import fixture, raises

from idsse.common.validate_schema import get_validator


@fixture
def available_data_validator() -> Validator:
    schema_name = 'das_available_data_schema'
    return get_validator(schema_name)


@fixture
def data_request_validator() -> Validator:
    schema_name = 'das_data_request_schema'
    return get_validator(schema_name)


@fixture
def criteria_validator() -> Validator:
    schema_name = 'criteria_schema'
    return get_validator(schema_name)


@fixture
def criteria_message() -> dict:
    return {
        "corrId": {
            "originator": "IDSSe",
            "uuid": "4899d220-beec-467b-a0e6-9d215b715b97",
            "issueDt": "2022/10/07 14:00:00"
        },
        "issueDt": "2022/10/07 14:00:00",
        "location": {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "The spot",
                        "radius": 3.00
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            -106.62312540068922,
                            34.964261450738306
                        ]
                    }
                }
            ]
        },
        "validDt": {
            "start": "2022/10/08 0:00:00",
            "end": "2022/10/08 12:00:00"
        },
        "conditions": [
            {
                "severity": "MODERATE",
                "combined": "A AND B",
            },
        ],
        "data": {
            "A": {
                "arealPercentage": 0,
                "duration": 0,
                "product": {
                    "fcst": [
                        "NBM"
                    ]
                },
                "field": "DEW POINT",
                "units": "Fahrenheit",
                "relational": "LESS THAN",
                "thresh": 60,
                "mapping": {
                    "min": 35.0,
                    "max": 75.0,
                    "clip": "true"
                }
            },
            "B": {
                "arealPercentage": 0,
                "duration": 0,
                "product": {
                    "fcst": [
                        "NBM"
                    ]
                },
                "field": "RELATIVE HUMIDITY",
                "units": "PERCENT",
                "relational": "GREATER THAN",
                "thresh": 30,
                "mapping": {
                    "min": 0.0,
                    "max": 75.0,
                    "clip": "true"
                }
            }
        },
        "tags": {
            "values": [
            ],
            "keyValues": {
                "name": "Abq Rain",
                "nwsOffice": "BOU"
            }
        }
    }



def test_validate_das_issue_request(available_data_validator: Validator):
    message = {'sourceType': 'issue',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'field': 'TEMP',
                             }}
    try:
        available_data_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_issue_request(available_data_validator: Validator):
    # message is missing 'region'
    message = {'sourceType': 'field',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'field': 'TEMP',
                             'valid': '2022-01-02T15:00:00.000Z'
                             }}
    with raises(ValidationError):
        available_data_validator.validate(message)


def test_validate_das_valid_request(available_data_validator: Validator):
    message = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    try:
        available_data_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_valid_request(available_data_validator: Validator):
    # message is missing 'field'
    message = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    with raises(ValidationError):
        available_data_validator.validate(message)


def test_validate_das_lead_request(available_data_validator: Validator):
    message = {'sourceType': 'lead',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    try:
        available_data_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_lead_request(available_data_validator: Validator):
    # message is missing 'product'
    message = {'sourceType': 'valid',
               'sourceObj': {'region': 'PR',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z'
                             }}
    with raises(ValidationError):
        available_data_validator.validate(message)


def test_validate_das_field_request(available_data_validator: Validator):
    message = {'sourceType': 'field',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'field': 'TEMP',
                             'issue': '2022-01-02T12:00:00.000Z',
                             'valid': '2022-01-02T15:00:00.000Z'
                             }}
    try:
        available_data_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_field_request(available_data_validator: Validator):
    # message is missing 'issue'
    message = {'sourceType': 'field',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'PR',
                             'field': 'TEMP',
                             'valid': '2022-01-02T15:00:00.000Z'
                             }}
    with raises(ValidationError):
        available_data_validator.validate(message)


def test_validate_das_data_request(data_request_validator: Validator):
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
    try:
        data_request_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_data_request(data_request_validator: Validator):
    # missing product
    message = {
        'sourceType': 'data',
        'sourceObj': {
            'region': 'CO',
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
                    'region': 'CO',
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
                    'region': 'CO',
                    'issue': '2022-01-02T12:00:00.000Z',
                    'valid': '2022-01-02T15:00:00.000Z',
                    'field': 'TEMP'
                }
            }
        }
    }
    with raises(ValidationError):
        data_request_validator.validate(message)


def test_validate_das_opr_with_multi_sources_request(data_request_validator: Validator):
    # this is an example of a logical join operator, the operator itself is not validated
    message = {
        "sourceType": "join",
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
        "label": ("AND(NBM:TEMP:Fahrenheit:LT:60.000:35.000:75.000:true, "
                  "NBM:WINDSPEED:MilesPerHour:GT:3.000:0.000:5.000:true)")
    }
    try:
        data_request_validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_bad_opr_with_multi_sources_request(data_request_validator: Validator):
    # one of the operator object does not contains 'source', has 'not_source' instead
    message = {
        "sourceType": "join",
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
                    "not_source": {
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
        "label": ("AND(NBM:TEMP:Fahrenheit:LT:60.000:35.000:75.000:true, "
                  "NBM:WINDSPEED:MilesPerHour:GT:3.000:0.000:5.000:true)")
    }
    with raises(ValidationError):
        data_request_validator.validate(message)


def test_validate_criteria_message(criteria_validator, criteria_message):
    try:
        criteria_validator.validate(criteria_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_criteria_message_conditions(criteria_validator, criteria_message):
    criteria_message.pop('conditions')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


def test_validate_criteria_message_with_missing_name(criteria_validator, criteria_message):
    criteria_message['tags']['keyValues'].pop('name')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


def test_validate_criteria_message_with_bad_product_type(criteria_validator, criteria_message):
    product = criteria_message['data']['A']['product']
    product['not_fcst_or_obs'] = product.pop('fcst')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


def test_validate_criteria_message_with_bad_mapping(criteria_validator, criteria_message):
    mapping = criteria_message['data']['B']['mapping']
    mapping['smallest'] = mapping.pop('min')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


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

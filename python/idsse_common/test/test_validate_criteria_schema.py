'''Test suite for criteria message using validate_schema.py'''
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
def criteria_validator() -> Validator:
    schema_name = 'criteria_schema'
    return get_validator(schema_name)


@fixture
def simple_criteria_message() -> dict:
    return {
        "corrId": {
            "originator": "IDSSe",
            "uuid": "4899d220-beec-467b-a0e6-9d215b715b97",
            "issueDt": "2022-11-11T14:00:00.000Z"
        },
        "issueDt": "2022-11-11T14:00:00.000Z",
        "location": {
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Abq"
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-106.62312540068922, 34.964261450738306]
                    }
                }
            ]
        },
        "validDt": {
            "start": "2022-11-12T00:00:00.000Z",
            "end": "2022-11-12T00:00:00.000Z"
        },
        "conditions": [
            {
                "name": "Above Freeze Temp",
                "severity": "MODERATE",
                "combined": "A",
                "partsUsed": ["A"]
            }
        ],
        "parts": [
            {
                "name": "A",
                "duration": 0,
                "arealPercentage": 0,
                "product": {
                    "fcst": [
                        "NBM"
                    ]
                },
                "field": "TEMPERATURE",
                "units": "DEG F",
                "region": "CONUS",
                "relational": "GREATER THAN",
                "thresh": 30,
                "mapping": {
                    "min": 0.0,
                    "max": 75.0,
                    "clip": "true"
                }
            }
        ],
        "tags": {
            "values": [
            ],
            "keyValues": {
                "name": "Abq Temp",
                "nwsOffice": "BOU"
            }
        }
    }


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
                        "coordinates": [-106.62312540068922, 34.964261450738306]
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
                "name": "Two part Condition",
                "severity": "MODERATE",
                "combined": "A AND B",
                "partsUsed": ["A", "B"]
            },
        ],
        "parts": [
            {
                "name": "A",
                "arealPercentage": 0,
                "duration": 0,
                "product": {
                    "fcst": [
                        "NBM"
                    ]
                },
                "field": "DEW POINT",
                "units": "Fahrenheit",
                "region": "CONUS",
                "relational": "LESS THAN",
                "thresh": 60,
                "mapping": {
                    "min": 35.0,
                    "max": 75.0,
                    "clip": "true"
                }
            },
            {
                "name": "B",
                "arealPercentage": 0,
                "duration": 0,
                "product": {
                    "fcst": [
                        "NBM"
                    ]
                },
                "field": "RELATIVE HUMIDITY",
                "units": "PERCENT",
                "region": "CONUS",
                "relational": "GREATER THAN",
                "thresh": 30,
                "mapping": {
                    "min": 0.0,
                    "max": 75.0,
                    "clip": "true"
                }
            }
        ],
        "tags": {
            "values": [
            ],
            "keyValues": {
                "name": "Abq Rain",
                "nwsOffice": "BOU"
            }
        }
    }


def test_validate_simple_criteria_message(criteria_validator: Validator,
                                          simple_criteria_message: dict):
    try:
        criteria_validator.validate(simple_criteria_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_criteria_message(criteria_validator: Validator, criteria_message: dict):
    try:
        criteria_validator.validate(criteria_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_criteria_message_without_conditions(criteria_validator: Validator,
                                                      criteria_message: dict):
    criteria_message.pop('conditions')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


def test_validate_criteria_message_with_missing_name(criteria_validator: Validator,
                                                     criteria_message: dict):
    criteria_message['tags']['keyValues'].pop('name')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


def test_validate_criteria_message_with_bad_product_type(criteria_validator: Validator,
                                                         criteria_message: dict):
    product = criteria_message['parts'][0]['product']
    product['not_fcst_or_obs'] = product.pop('fcst')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)


def test_validate_criteria_message_with_bad_mapping(criteria_validator: Validator,
                                                    criteria_message: dict):
    mapping = criteria_message['parts'][1]['mapping']
    mapping['smallest'] = mapping.pop('min')
    with raises(ValidationError):
        criteria_validator.validate(criteria_message)

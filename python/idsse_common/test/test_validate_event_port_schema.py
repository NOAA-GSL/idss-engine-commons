'''Test suite for event port message using validate_schema.py'''
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
def event_port_validator() -> Validator:
    schema_name = 'event_portfolio_schema'
    return get_validator(schema_name)


@fixture
def simple_event_port_message() -> dict:
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
                        "name": "Location 1"
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
                "name": "Abq TEMP",
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
                "region": "CO",
                "product": {
                    "fcst": [
                        "NBM"
                    ]
                },
                "field": "TEMPERATURE",
                "units": "DEG F",
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
                "Abq Temp"
            ],
            "keyValues": {
                "name": "Abq TEMP",
                "nwsOffice": "BOU"
            }
        },
        "riskResults": [
            {
                "evaluatedAt": "2022-11-11T14:54:32.100Z",
                "conditionKey": "Abq TEMP",
                "productKey": "NBM",
                "locationKey": "Single Location",
                "validDt": [
                    "2022-11-12T00:00:00.000Z"
                ],
                "data": [
                    {
                        "name": "Abq TEMP",
                        "type": "condition",
                        "singleValue": [
                            0.18964463472366333
                        ],
                        "geoDist": [
                            {
                                "0.18964463472366333": 1
                            }
                        ]
                    },
                    {
                        "name": "A",
                        "type": "criteria",
                        "singleValue": [
                            0.18964463472366333
                        ],
                        "geoDist": [
                            {
                                "0.18964463472366333": 1
                            }
                        ]
                    },
                    {
                        "name": "A",
                        "type": "raw",
                        "singleValue": [
                            38.53400802612305
                        ],
                        "geoDist": [
                            {
                                "38.53400802612305": 1
                            }
                        ]
                    }
                ],
                "metaData": [
                    {
                        "name": "Abq TEMP",
                        "type": "condition",
                        "states": [
                            {
                                "durationInMin": 0,
                                "min": 0.18964463472366333,
                                "minAt": "2022-11-12T00:00:00.000Z",
                                "max": 0.18964463472366333,
                                "startDt": "2022-11-12T00:00:00.000Z",
                                "endDt": "2022-11-12T00:00:00.000Z",
                                "maxAt": "2022-11-12T00:00:00.000Z",
                                "criteriaMet": "true"
                            }
                        ]
                    },
                    {
                        "name": "A",
                        "type": "criteria",
                        "states": [
                            {
                                "durationInMin": 0,
                                "min": 0.18964463472366333,
                                "minAt": "2022-11-12T00:00:00.000Z",
                                "max": 0.18964463472366333,
                                "startDt": "2022-11-12T00:00:00.000Z",
                                "endDt": "2022-11-12T00:00:00.000Z",
                                "maxAt": "2022-11-12T00:00:00.000Z",
                                "criteriaMet": "true"
                            }
                        ]
                    }
                ]
            }
        ]
    }


def test_validate_event_port_message(event_port_validator: Validator,
                                     simple_event_port_message: dict):
    try:
        event_port_validator.validate(simple_event_port_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_event_port_message_without_results(event_port_validator: Validator,
                                                     simple_event_port_message: dict):
    simple_event_port_message.pop('riskResults')
    with raises(ValidationError):
        event_port_validator.validate(simple_event_port_message)


def test_validate_event_port_message_with_bad_geo_dist(event_port_validator: Validator,
                                                       simple_event_port_message: dict):
    criteria_geo_dist = simple_event_port_message['riskResults'][0]['data'][0]['geoDist']
    criteria_geo_dist.append({"not a number": 3})
    with raises(ValidationError):
        event_port_validator.validate(simple_event_port_message)


def test_validate_event_port_message_with_missing_metadata(event_port_validator: Validator,
                                                           simple_event_port_message: dict):
    simple_event_port_message['riskResults'][0]['metaData'][0]['states'].clear()
    with raises(ValidationError):
        event_port_validator.validate(simple_event_port_message)


def test_validate_event_port_message_with_missing_type_in_metadata(event_port_validator: Validator,
                                                                   simple_event_port_message: dict):
    simple_event_port_message['riskResults'][0]['metaData'][0].pop('type')
    with raises(ValidationError):
        event_port_validator.validate(simple_event_port_message)

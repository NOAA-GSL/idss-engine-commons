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
# cspell:ignore geodist

import random
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
def event_port_validator() -> Validator:
    schema_name = 'event_portfolio_schema'
    return get_validator(schema_name)


@fixture
def new_data_validator() -> Validator:
    schema_name = 'new_data_schema'
    return get_validator(schema_name)


@fixture
def das_web_request_validator() -> Validator:
    schema_name = 'das_web_request_schema'
    return get_validator(schema_name)


@fixture
def das_web_response_validator() -> Validator:
    schema_name = 'das_web_response_schema'
    return get_validator(schema_name)


@fixture
def das_data_message() -> dict:
    return {
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
                        "coordinates": [
                            -106.62312540068922,
                            34.964261450738306
                        ]
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
                "combined": "A"
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
                "region": "CO",
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
                "region": "CO",
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
                "region": "CO",
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


@fixture
def simple_event_port_message() -> dict:
    return {
        "timeStamp": "2023-09-27T17:25:36.000Z",
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
                        "coordinates": [
                            -106.62312540068922,
                            34.964261450738306
                        ]
                    }
                }
            ]
        },
        "validDt": {
            "start": "2022-11-12T0:00:00.000Z",
            "end": "2022-11-12T0:00:00.000Z"
        },
        "conditions": [
            {
                "name": "Above Freeze Temp",
                "severity": "MODERATE",
                "combined": "A"
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
                "region": "CO",
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
        },
        "riskResults": [
            {
                "conditionKey": "Above Freeze Temp",
                "locationKey": "Abq",
                "productKey": "NBM",
                "validDt": ["2022-11-12T00:00:00.000Z"],
                "data": [
                    {
                        "name": "condition: Above Freeze Temp",
                        "type": "criteria",
                        "singleValue": [0.18964463472366333],
                        "geoDist": [{"0.18964463472366333": 1}]
                    },
                    {
                        "name": "part: A",
                        "type": "raw",
                        "singleValue": [38.53400802612305],
                        "geoDist": [{"38.53400802612305": 1}]
                    }
                ],
                "metaData": [
                    {
                        "name": "condition: Above Freeze Temp",
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


@fixture
def new_field_message() -> dict:
    return {
        "product": "NBM",
        "region": "CO",
        "issueDt": "2023-09-15T16:00:00.000Z",
        "validDt": "2023-09-17T06:00:00.000Z",
        "field": "TEMP"
    }


@fixture
def new_valid_message() -> dict:
    return {
        "product": "NBM",
        "region": "CO",
        "issueDt": "2023-09-15T16:00:00.000Z",
        "validDt": "2023-09-17T06:00:00.000Z",
        "field": ["TEMP", "WINDSPEED"]
    }


@fixture
def new_issue_message() -> dict:
    return {
        "product": "NBM",
        "region": "CO",
        "issueDt": "2023-09-15T16:00:00.000Z",
        "field": {
            "2023-09-15T17:00:00.000Z": ["TEMP", "WINDSPEED"],
            "2023-09-15T18:00:00.000Z": ["TEMP", "WINDSPEED"],
            "2023-09-15T19:00:00.000Z": ["TEMP", "WINDSPEED"],
            "2023-09-15T20:00:00.000Z": ["TEMP", "WINDSPEED"]
        }
    }


@fixture
def das_web_request_message() -> dict:
    return {
        "issueDt": "2023-01-10T08:00:00.000Z",
        "dataRequest": "A AND B",
        "parts": [
            {
                "name": "A",
                "duration": 0,
                "arealPercentage": 0,
                "product": "NBM",
                "field": "WINDSPEED",
                "units": "MilesPerHour",
                "region": "CO",
                "relational": "GREATER THAN",
                "thresh": 5,
                "mapping": {
                    "min": 0.0,
                    "max": 20.0,
                    "clip": "true"
                }
            },
            {
                "name": "B",
                "duration": 0,
                "arealPercentage": 0,
                "product": "NBM",
                "field": "TEMPERATURE",
                "units": "Fahrenheit",
                "region": "CO",
                "relational": "LESS THAN OR EQUAL",
                "thresh": 30,
                "mapping": {
                    "min": 15.0,
                    "max": 45.0,
                    "clip": "true"
                }
            }
        ],
        "valids": [
            "2023-01-11T06:00:00.000Z",
            "2023-01-11T07:00:00.000Z",
            "2023-01-11T08:00:00.000Z",
            "2023-01-11T09:00:00.000Z",
            "2023-01-11T10:00:00.000Z",
            "2023-01-11T11:00:00.000Z",
            "2023-01-11T12:00:00.000Z",
            "2023-01-11T13:00:00.000Z",
            "2023-01-11T14:00:00.000Z",
            "2023-01-11T15:00:00.000Z",
            "2023-01-11T16:00:00.000Z",
            "2023-01-11T17:00:00.000Z",
            "2023-01-11T18:00:00.000Z"
        ],
        "bbox": {
            "botLeft": [910, 829],
            "topRight": [1010, 929]
        }
    }


@fixture
def das_web_response_message() -> dict:
    return {
        "issueDt": "2023-01-10T08:00:00.000Z",
        "dataRequest": "A",
        "parts": [
            {
                "name": "A",
                "duration": 0,
                "arealPercentage": 0,
                "product": "NBM",
                "field": "WINDSPEED",
                "units": "MilesPerHour",
                "region": "CO",
                "relational": "GREATER THAN",
                "thresh": 5,
                "mapping": {
                    "min": 0.0,
                    "max": 20.0,
                    "clip": "true"
                }
            }
        ],
        "valids": [
            "2023-01-11T06:00:00.000Z",
            "2023-01-11T18:00:00.000Z"
        ],
        "bbox": {
            "botLeft": [100, 102],
            "topRight": [200, 202]
        },
        "data": {
            "2023-01-11T06:00:00.000Z": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ],
            "2023-01-11T18:00:00.000Z": [
                [9, 8, 7],
                [6, 5, 4],
                [3, 2, 1]
            ],
            "scale": 10
        }
    }


# tests
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


def test_validate_new_field_data_message(new_data_validator: Validator,
                                         new_field_message: dict):
    try:
        new_data_validator.validate(new_field_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_new_missing_field_data_message(new_data_validator: Validator,
                                                 new_field_message: dict):
    # convert a new field message to a missing field message by changing 'field' key to 'missing'
    new_field_message['missing'] = new_field_message.pop('field')
    try:
        new_data_validator.validate(new_field_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_new_field_data_message_missing_region(new_data_validator: Validator,
                                                        new_field_message: dict):
    new_field_message.pop('region')
    with raises(ValidationError):
        new_data_validator.validate(new_field_message)


def test_validate_new_valid_data_message(new_data_validator: Validator,
                                         new_valid_message: dict):
    try:
        new_data_validator.validate(new_valid_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_new_missing_valid_data_message(new_data_validator: Validator,
                                                 new_valid_message: dict):
    # convert new valid to missing valid by putting a field in missing list
    fields = new_valid_message['field']
    new_valid_message['field'] = fields[:-1]
    new_valid_message['missing'] = [fields[-1]]
    try:
        new_data_validator.validate(new_valid_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_new_valid_data_message_bad_field(new_data_validator: Validator,
                                                   new_valid_message: dict):
    new_valid_message['field'].append('BAD_FIELD_NAME')
    with raises(ValidationError):
        new_data_validator.validate(new_valid_message)


def test_validate_new_issue_data_message(new_data_validator: Validator,
                                         new_issue_message: dict):
    try:
        new_data_validator.validate(new_issue_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_new_missing_issue_data_message(new_data_validator: Validator,
                                                 new_issue_message: dict):
    # convert new issue to missing issue by putting some fields in missing object
    fields = new_issue_message['field']
    found = {}
    missing = {}
    for valid_key in fields:
        if random.randint(0, 1):
            found[valid_key] = fields[valid_key]
            missing[valid_key] = []
        else:
            found[valid_key] = []
            missing[valid_key] = fields[valid_key]

    new_issue_message['field'] = found
    new_issue_message['missing'] = missing
    try:
        new_data_validator.validate(new_issue_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_new_issue_data_message_bad_valid_string(new_data_validator: Validator,
                                                          new_issue_message: dict):
    # grab a good list of fields from the message
    sample_fields = next(iter(new_issue_message['field'].values()))
    # use the good list but with a bad valid string
    new_issue_message['field']['Not a string rep of a valid date'] = sample_fields
    with raises(ValidationError):
        new_data_validator.validate(new_issue_message)


def test_validate_das_web_request_message(das_web_request_validator: Validator,
                                          das_web_request_message: dict):
    try:
        das_web_request_validator.validate(das_web_request_message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'


def test_validate_das_web_request_message_bad_bbox(das_web_request_validator: Validator,
                                                   das_web_request_message: dict):
    # replace the bottom left int coordinate with a float
    das_web_request_message['bbox']['botLeft'][0] = 1.2
    with raises(ValidationError):
        das_web_request_validator.validate(das_web_request_message)


def test_validate_das_web_request_message_multi_product(das_web_request_validator: Validator,
                                                        das_web_request_message: dict):
    # replace the single product with multiple product structure (like in criteria and eventPort)
    das_web_request_message['parts'][0]['product'] = {
        "fcst": [
            "NBM"
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


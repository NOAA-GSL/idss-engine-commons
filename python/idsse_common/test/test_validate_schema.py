"""Test suite for validate_schema.py"""
# ----------------------------------------------------------------------------------
# Created on Fri Aug 04 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------

from datetime import datetime, timezone, timedelta

from jsonschema.exceptions import ValidationError
import pytest

from idsse.common.validate_schema import get_validator

# pylint: disable=missing-function-docstring


def test_validate_das_valid_request():
    request = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'CO',
                             'issueDt': '2022-01-02T12:00:00.000Z',
                             'field': 'TEMP'}}
    assert request


def test_validate_good_criteria_message():
    message = {"corrId": {"originator": "IDSSe",
                          "issueDt": "_",
                          "uuid": "dc7ad8c1-5ff2-416f-9fee-66c598256189"},
               "issueDt": "2018-11-13T20:20:39+00:00",
               "validDt": {"start": "2018-11-13T21:20:39+00:00",
                           "end": "2018-11-13T23:20:39+00:00"},
               "tags": {"values": ["bob", "uncle"], "keyValues": {}},
               "location": {"features": [{"type": "Feature",
                                          "properties": {"innerRadius": 3,
                                                         "outerRadius": 4},
                                          "geometry": {
                                              "type": "Point",
                                              "coordinates": [
                                                  -105.10392834544123,
                                                  40.16676831094053]}}],
                            "buffer": 1,
                            "bufferUnits": "miles"}}

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
    message = {"product": "NBM",
               "issueDt": "2023-2-11T14:00:00.000Z",
               "validDt": "2023-2-11T20:00:00.000Z",
               "field": ["TEMP", "WINDSPEED"]}

    schema_name = 'new_data_schema'
    validator = get_validator(schema_name)
    try:
        validator.validate(message)
    except ValidationError as exc:
        assert False, f'Validate message raised an exception {exc}'

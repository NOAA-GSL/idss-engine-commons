'''Test suite for new data message using validate_schema.py'''
# ----------------------------------------------------------------------------------
# Created on Mon Nov 20 2023
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
def new_data_validator() -> Validator:
    schema_name = 'new_data_schema'
    return get_validator(schema_name)


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

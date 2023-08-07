"""Class for validating IDSSe JSON messages against schema"""
# ----------------------------------------------------------------------------------
# Created on Mon Aug 07 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------
import json
import os
from typing import Optional

from jsonschema import Validator, validate, FormatChecker, RefResolver
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validator_for


def _test_variable():
    # NewData should broadcast a "Variable", except that "Variable" allows empty fields.
    # If you look in variable.json, you'll see TEMP and WINDSPEED are currently the only field names
    schema = json.loads(open('src/schema/variable.json', 'r', encoding='utf8').read())
    schema['allOf'] = [{"$ref": "#/Variable"}]

    # use this if you want to enforce that fields in NOT empty
    # schema['allOf'] = [{"$ref": "#/Variable"},
    #                    {"properties": {"field": {"minItems": 1}}}]

    message = {"product": "NBM",
               "issueDt": "2023-2-11T14:00:00.000Z",
               "validDt": "2023-2-11T20:00:00.000Z",
               "field": ["TEMP", "WINDSPEED"]}

    try:
        validate(instance=message, schema=schema)
        print('GOOD JSON')
    except ValidationError as exc:
        print("BAD JSON")
        print(exc)


def _get_refs(json_obj: dict, result: Optional[set] = None) -> set:
    if result is None:
        result = set()
    for key, value in json_obj.items():
        if key == '$ref':
            idx = value.index('#/')
            if idx > 0:
                result.add(value[:idx])
        elif isinstance(value, dict):
            _get_refs(value, result)
    return result


def get_validator(schema_name) -> Validator:
    """Get a jsonschema Validator to be used when evaluating json messages against specified schema

    Args:
        schema_name (str): The name of the message schema,
                           must exist under idss-engine-common/schema

    Returns:
        Validator: A validator loaded with schema and all dependencies
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    schema_dir = os.path.join(os.path.sep, *(current_path.split(os.path.sep)[:-4]), 'schema')
    schema_filename = os.path.join(schema_dir, schema_name+'.json')
    with open(schema_filename, 'r', encoding='utf8') as file:
        schema = json.load(file)

    base = json.loads('{"$schema": "http://json-schema.org/draft-07/schema#"}')

    dependencies = {base.get('$id'): base}
    refs = _get_refs(schema)
    while len(refs):
        new_refs = set()
        for ref in refs:
            schema_filename = os.path.join(schema_dir, ref)
            with open(schema_filename, 'r', encoding='utf8') as file:
                ref_schema = json.load(file)
            dependencies[ref_schema.get('$id', ref)] = ref_schema
            new_refs = _get_refs(ref_schema, new_refs)
        refs = {ref for ref in new_refs if ref not in dependencies}

    resolver = RefResolver.from_schema(schema=base,
                                       store=dependencies)

    return validator_for(base)(schema, resolver=resolver, format_checker=FormatChecker())


def _test_criteria():
    schema_name = 'test_schema'
    validator = get_validator(schema_name)

    try:
        validator.validate(instance={"corrId": {"originator": "IDSSe",
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
                                                  "bufferUnits": "miles"}})
        print("GOOD JSON")
    except ValidationError as exc:
        print("BAD JSON")
        print(exc)


def _test_new_data():
    schema_name = 'new_data_schema'
    validator = get_validator(schema_name)

    try:
        validator.validate(instance={"product": "NBM",
                                     "issueDt": "2023-2-11T14:00:00.000Z",
                                     "validDt": "2023-2-11T20:00:00.000Z",
                                     "field": ["TEMP", "WINDSPEED"]})
        print("GOOD JSON")
    except ValidationError as exc:
        print("BAD JSON")
        print(exc)


if __name__ == '__main__':
    _test_criteria()
    # _test_new_data()

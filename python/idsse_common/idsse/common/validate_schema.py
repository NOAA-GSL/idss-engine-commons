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
from typing import Optional, Union

# pylint: disable=no-name-in-module
from jsonschema import Validator, FormatChecker, RefResolver
from jsonschema.validators import validator_for


def _get_refs(json_obj: Union[dict, list], result: Optional[set] = None) -> set:
    if result is None:
        result = set()
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == '$ref':
                idx = value.index('#/')
                if idx > 0:
                    result.add(value[:idx])
            else:
                _get_refs(value, result)
    elif isinstance(json_obj, list):
        for item in json_obj:
            _get_refs(item, result)
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
    schema_dir = os.path.join(current_path, 'schema')
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

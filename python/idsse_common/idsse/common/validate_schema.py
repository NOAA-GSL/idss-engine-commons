"""Test python validator driver"""
import json

from jsonschema import validate, FormatChecker, RefResolver
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validator_for


def _sample():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name"],
    }

    validate(instance={"name": "John", "age": 30}, schema=schema)
    # No error, the JSON is valid.

    validate(instance={"name": "John", "age": "30"}, schema=schema)
    # ValidationError: '30' is not of type 'number'

    validate(instance={"name": "John"}, schema=schema)
    # No error, the JSON is valid.

    validate(instance={"age": 30}, schema=schema)
    # ValidationError: 'name' is a required property

    validate(instance={"name": "John", "age": 30, "job": "Engineer"}, schema=schema)
    # No error, the JSON is valid. By additional fields are allowed.


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


def _test_criteria():
    base = json.loads('{"$schema": "http://json-schema.org/draft-07/schema#"}')
    timing = json.loads(open('src/schema/timing.json', 'r', encoding='utf8').read())
    tags = json.loads(open('src/schema/tags.json', 'r', encoding='utf8').read())
    geometry = json.loads(open('src/schema/geometry.json', 'r', encoding='utf8').read())
    location = json.loads(open('src/schema/location.json', 'r', encoding='utf8').read())

    schema_store = {
        base.get('$id'): base,
        timing.get('$id', 'timing.json'): timing,
        tags.get('$id', 'tags.json'): tags,
        geometry.get('$id', 'geometry.json'): geometry,
        location.get('$id', 'location.json'): location,
    }

    resolver = RefResolver.from_schema(schema=base,
                                       store=schema_store)

    filename = 'src/schema/test_schema.json'
    print(filename)
    with open(filename, 'r', encoding='utf8') as file:
        schema = json.load(file)
    print(schema)

    validator = validator_for(base)(schema, resolver=resolver, format_checker=FormatChecker())

    try:
        validator.validate(instance={"originator": "IDSSe",
                                     "uuid": "dc7ad8c1-5ff2-416f-9fee-66c598256189",
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


def _test_das_request():
    base = json.loads('{"$schema": "http://json-schema.org/draft-07/schema#"}')
    variable = json.loads(open('src/schema/variable.json', 'r', encoding='utf8').read())

    schema_store = {
        base.get('$id'): base,
        variable.get('$id', 'variable.json'): variable,
    }

    resolver = RefResolver.from_schema(schema=base,
                                       store=schema_store)

    filename = 'src/schema/das_request.json'
    print(filename)
    with open(filename, 'r', encoding='utf8') as file:
        schema = json.load(file)
    print(schema)

    validator = validator_for(base)(schema, resolver=resolver, format_checker=FormatChecker())

    try:
        validator.validate(instance={"sourceType": "issue",
                                     "sourceObj": {"product": "NBM",
                                                   "field": "TEMP"}})
        print("GOOD JSON")
    except ValidationError as exc:
        print("BAD JSON")
        print(exc)


if __name__ == '__main__':
    _test_variable()

===========
JSON Schema
===========

Goals:
======
Document and Validate all JSON messages used to communicate between microservices within IDSS Engine.

Additional Goal:
----------------
The different message types should share as much structure in common as is practical. This consistency
should increase human readability, as developers become familiar with standard, and reduce complexity
for message handling.

Resources:
==========
- `JSON schema <https://json-schema.org/>`_
- `Understanding JSON schema <https://json-schema.org/understanding-json-schema/>`_

Convention/Patterns:
====================
- Auxiliary or Subschema are used to group related objects. Subschema objects are defined at the root 
  level in json files. The filename is based on the dominant object.

Timing.json::
{
    "TimeString": {
        "description": "String representation of a date/time",
        "type": "string",
        "format": "date-time"
    },
    "TimeList": {
        "description": "A list of specific time_string(s)",
        "type": "array",
        "items": {"$ref": "#/TimeString"},
        "minItems": 1
    },
    "TimeRange": {
        "description": "Date/time string specifying the start and end date/ times",
        "type": "object",
        "properties": {
        "start": {"$ref": "#/TimeString"},
        "end": {"$ref": "#/TimeString"}
        },
        "required": [
        "start",
        "end"
        ]
    },
    "Timing": {
        "description": "Either a TimeString, TimeList, or TimeRange",
        "oneOf": [
        {"$ref": "#/TimeString"},
        {"$ref": "#/TimeList"},
        {"$ref": "#/TimeRange"}
        ]
    }
}


- Schemas that define a message should, for the most part, be entirely built from subschema. The 
  filename should represent the message type and end with _schema in order to distinguish from 
  subschema.

*(These examples are not complete, thus will need to be updated)*

New_data_schema.json *(this currently is only a partial schema, new data service publishes other information)*

One of the messages that the new_data service publishes indicates when a field from a product source 
is available for a specific issue/valid datetime. Basically this is a message specifying the Variable 
subschema, except that a Variable does NOT require a Field *(it is optional)*. Thus the new_data message 
utilized the Variable subschema and adds the additional requirement that there must be at least one 
field.::

{
    "type": "object",
    "allOf": [
        {"$ref": "variable.json#/Variable"},
        {"properties": {"field": {"minItems": 1}}}
    ]
}


Criteria_schema.json *(this is incomplete, there is more in a criteria message, but is a 
good example of how a message is built from subschemas)*::

{
    "type": "object",
    "properties": {
        "corrId": {"$ref": "corr_id.json#/CorrId"},
        "issueDt": {"$ref": "timing.json#/Timing"},
        "tags": {"$ref": "tags.json#/Tags"},
        "validDt": {"$ref": "timing.json#/Timing"},
        "location": {"$ref": "location.json#/Location"}
    },
    "required": [
        "corrId",
        "issueDt",
        "tags",
        "validDt",
        "location"
    ]
}

Correlation ID
==============

A Correlation ID, also known as a Transit ID, is a unique identifier value that is attached to requests and
messages that allow reference to a particular transaction or event chain. Without a correlation ID, developers
would have to spend much time and make errors trying to piece together a request's path through the system.
Correlation ID improves the process by assigning a unique identifier to each request, which can then be used
to track the request as it makes its way through the system.

Correlation ID in IDSSe
-----------------------

Typically correlation id is simple a uuid; however since most of the focus of IDSSe is in addressing criteria(s)
(or Support Profiles from IMS) which each have an associated uuid, IDSSe adds two additional pieces of information.
The first is the system (or service) that created the correlation id, and the second is the specific issue datetime that
is being addressed. So if a criteria is generated from an IMS Support Profile, the correlation id will specify IMS
as the originator, the uuid assigned to that Support Profile by IMS, and the nominal current issue datetime of the
forecast(s). If the work in a message is not related to a criteria (Support Profile) a system initiating the request
will identify its self as the originator, generate a uuid, and specify an issue datetime (or if there is no
meaningful issue datetime, indicate that situation by using a single underscore '_' in place of the issue datetime.
See examples

Additionally these Correlation IDs should be included in logging messages.
See logging

Examples
========

Each json message should contain keyed correlation ID object:

    "corrId": {
        "issueDt": "2022-11-11T14:00:00.000Z",
        "originator": "New_Data_Service",
        "uuid": "ce9b40dc-883e-11ec-a523-dca90491e142"
    },
    
If the message is related to an IMS Support Profile: 
    
    "corrId": {
        "issueDt": "2023-01-15T14:00:00.000Z",
        "originator": "IMS_gateway",
        "uuid": "a1eca3de-2796-4bc5-b63b-8ba2d171de6a2"
    },
    
And for messages related to the same IMS Support Profile, but for the next issue datetime:

    "corrId": {
        "issueDt": "2023-01-15T15:00:00.000Z",
        "originator": "IMS_gateway",
        "uuid": "a1eca3de-2796-4bc5-b63b-8ba2d171de6a2"
    },
    
If the message has not associated with any (or a singular) issue datetime:
    
    "corrId": {
        "issueDt": "_",
        "originator": "Criteria_Manager",
        "uuid": "76ef820d-0f51-44b6-a7b6-77252a06b2c7"
    },
    
And if at some point during the process a specific issue datetime is relevant the work started by previous message:
    
    "corrId": {
        "issueDt": "2023-04-1T00:00:00.000Z",
        "originator": "Criteria_Manager",
        "uuid": "76ef820d-0f51-44b6-a7b6-77252a06b2c7"
    },

    
Tools
=====

Python
------

Sample code::

    from idsse.common.json_message import get_corr_id, add_corr_id
    from idsse.common.log_util import (get_default_log_config,
                                       get_corr_id_context_var_parts,
                                       set_corr_id_context_var)

    # Should read corr_id from request if possible
    corr_id = get_corr_id(request)
    
    # If correlation ID is not found in request one should be generated
    if not corr_id:
        corr_id = #TODO

    # After processing request and getting response, this will add a correlation ID to response
    response = process_request(request)
    response = add_corr_id(response, *corr_id)

    # Including Correlation ID to logging
    
    # When corr_id is in request message add it to logging context variable 
    if corr_id:
        set_corr_id_context_var(*corr_id)

    else:  # else create new corr_id as follows
        set_corr_id_context_var('Current_Service_Name')

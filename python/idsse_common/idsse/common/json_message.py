"""A module for managing the json messages used to communicate between services"""
# ------------------------------------------------------------------------------
# Created on Tue May 09 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary Layne
#
# ------------------------------------------------------------------------------

import json
from typing import Tuple, Union, Optional
from uuid import uuid4, UUID


def get_corr_id(
    message: Union[str, dict]
) -> Optional[Tuple[Optional[str], Optional[Union[UUID, str]], Optional[str]]]:
    """Extract the correlation id from a json message.
       The correlation id is made of three parts: originator, uuid, issue date/time

    Args:
        message (Union[str, json]): The message to be searched as either a string or json obj

    Returns:
        Optional[Tuple[Optional[str], Optional[Union[UUID, str]], Optional[str]]]:
            A tuple containing originator, uuid, and issue date/time, or None if a given part
            was not found. Returns simply None if no parts found
    """
    if isinstance(message, str):
        message = json.loads(message)

    corr_id = message.get('corrId', None)
    if not corr_id:
        return corr_id

    corr_id = (corr_id.get('originator', None),
               corr_id.get('uuid', None),
               corr_id.get('issueDt', None))

    if any(corr_id):
        return corr_id
    return None


def add_corr_id(message: Union[dict, str],
                originator: str,
                uuid_: Optional[Union[UUID, str]] = None,
                issue_dt: Optional[str] = None) -> dict:
    """Add (or overwrites) the three part correlation id to a json message

    Args:
        message (Union[dict, str]): The message to be updated
        originator (str): String representation of the originating service
        uuid_ (Union[UUID, str], optional): A UUID. Defaults to None.
        issue_dt (str, optional): The specific issue date/time associated with the message.
                                  Defaults to None.

    Returns:
        dict: The json message in dictionary form
    """
    if isinstance(message, str):
        message = json.loads(message)

    if not uuid_:
        uuid_ = uuid4()
    if not issue_dt:
        issue_dt = '_'
    message['corrId'] = {'originator': originator,
                         'uuid': f'{uuid_}',
                         'issueDt': issue_dt}

    return message

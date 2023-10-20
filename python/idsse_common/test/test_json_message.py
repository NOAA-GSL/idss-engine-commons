"""Test suite for json_message.py"""
# ----------------------------------------------------------------------------------
# Created on Fri Oct 20 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#    Mackenzie Grimes (2)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,protected-access
# pylint: disable=too-few-public-methods,unused-argument

import json
from datetime import datetime, UTC
from uuid import uuid4 as uuid

from idsse.common.json_message import get_corr_id, add_corr_id
from idsse.common.utils import to_iso

# test data
EXAMPLE_ORIGINATOR = 'idsse'
EXAMPLE_UUID = str(uuid())
EXAMPLE_ISSUE_DT = to_iso(datetime.now(UTC))

EXAMPLE_MESSAGE = {
    'corrId': {
        'originator': EXAMPLE_ORIGINATOR, 'uuid': EXAMPLE_UUID, 'issueDt': EXAMPLE_ISSUE_DT
    }
}


def test_get_corr_id_dict():
    result = get_corr_id(EXAMPLE_MESSAGE)
    assert result == (EXAMPLE_ORIGINATOR, EXAMPLE_UUID, EXAMPLE_ISSUE_DT)


def test_get_corr_id_str():
    result = get_corr_id(json.dumps(EXAMPLE_MESSAGE))
    assert result == (EXAMPLE_ORIGINATOR, EXAMPLE_UUID, EXAMPLE_ISSUE_DT)


def test_get_corr_id_empty_corr_id():
    result = get_corr_id({'other_data': 123})
    assert result is None


def test_get_corr_id_originator():
    result = get_corr_id({'corrId': {'originator': EXAMPLE_ORIGINATOR}})
    assert result == (EXAMPLE_ORIGINATOR, None, None)


def test_get_corr_id_uuid():
    result = get_corr_id({'corrId': {'uuid': EXAMPLE_UUID}})
    assert result == (None, EXAMPLE_UUID, None)


def test_get_corr_id_issue_dt():
    result = get_corr_id({'corrId': {'issueDt': EXAMPLE_ISSUE_DT}})
    assert result == (None, None, EXAMPLE_ISSUE_DT)


def test_json_get_corr_id_failure():
    bad_message = {'invalid': 'message'}
    result = get_corr_id(bad_message)
    assert result is None


def test_add_corr_id():
    new_originator = 'different_app'
    new_message = add_corr_id(EXAMPLE_MESSAGE, new_originator)

    # blank issueDt and random uuid should have been returned
    result = new_message['corrId']
    assert result['originator'] == new_originator
    assert result['issueDt'] == '_'
    assert result['uuid'] != EXAMPLE_UUID


def test_add_corr_id_str():
    new_originator = 'different_app'
    new_message = add_corr_id(json.dumps(EXAMPLE_MESSAGE), new_originator)
    assert new_message['corrId']['originator'] == new_originator


def test_add_corr_id_uuid():
    new_uuid = uuid()
    new_message = add_corr_id(EXAMPLE_MESSAGE, EXAMPLE_ORIGINATOR, uuid_=new_uuid)

    # blank issueDt and random uuid should have been returned
    assert new_message['corrId']['uuid'] == str(new_uuid)
    assert new_message['corrId']['originator'] == EXAMPLE_ORIGINATOR


def test_add_corr_id_issue_dt():
    new_issue = to_iso(datetime.now(UTC))
    new_message = add_corr_id(EXAMPLE_MESSAGE, EXAMPLE_ORIGINATOR, issue_dt=new_issue)
    assert new_message['corrId']['issueDt'] == new_issue

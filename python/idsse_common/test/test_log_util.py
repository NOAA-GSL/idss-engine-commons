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
# pylint: disable=missing-function-docstring,redefined-outer-name,invalid-name,unused-argument

import logging
import logging.config
from datetime import datetime, UTC
from uuid import uuid4 as uuid

from idsse.common.log_util import (
    set_corr_id_context_var,
    get_corr_id_context_var_parts,
    get_corr_id_context_var_str,
    get_default_log_config,
    AddCorrelationIdFilter
)
from idsse.common.utils import to_iso

logger = logging.getLogger(__name__)

# test data
EXAMPLE_ORIGINATOR = 'idsse'
EXAMPLE_UUID = uuid()
EXAMPLE_ISSUE_DT = datetime.now(UTC)
EXAMPLE_ISSUE_STR = to_iso(EXAMPLE_ISSUE_DT)
EXAMPLE_LOG_MESSAGE = 'hello world'


def test_add_correlation_id_filter():
    filter_object = AddCorrelationIdFilter()
    test_record = logging.LogRecord(
        name=EXAMPLE_ORIGINATOR,
        level=logging.INFO,
        pathname='./some/path/to/file.py',
        lineno=123,
        msg='hello world',
        args=None,
        exc_info=(None, None, None)
    )

    # corr_id does not exist yet, so filter fails
    assert not filter_object.filter(test_record)

    # set corr_id so filter does match
    set_corr_id_context_var(EXAMPLE_ORIGINATOR)
    assert filter_object.filter(test_record)


def test_set_corr_id():
    set_corr_id_context_var(EXAMPLE_ORIGINATOR, EXAMPLE_UUID, EXAMPLE_ISSUE_STR)

    expected_result = [EXAMPLE_ORIGINATOR, str(EXAMPLE_UUID), EXAMPLE_ISSUE_STR]
    assert get_corr_id_context_var_parts() == expected_result
    assert get_corr_id_context_var_str() == ';'.join(expected_result)


def test_set_corr_id_datetime():
    set_corr_id_context_var(EXAMPLE_ORIGINATOR, key=EXAMPLE_UUID, issue_dt=EXAMPLE_ISSUE_DT)

    assert get_corr_id_context_var_parts() == [
        EXAMPLE_ORIGINATOR, str(EXAMPLE_UUID), EXAMPLE_ISSUE_STR
    ]


def test_get_default_log_config_with_corr_id(capsys):
    logging.config.dictConfig(get_default_log_config('INFO'))
    corr_id = get_corr_id_context_var_str()

    logger.debug(msg=EXAMPLE_LOG_MESSAGE)
    stdout = capsys.readouterr().out  # capture std output from test run

    # should not be logging DEBUG if default log config handled level correctly
    assert stdout == ''
    logger.info(msg=EXAMPLE_LOG_MESSAGE)
    stdout = capsys.readouterr().out

    assert EXAMPLE_LOG_MESSAGE in stdout
    assert corr_id in stdout


def test_get_default_log_config_no_corr_id(capsys):
    logging.config.dictConfigClass(get_default_log_config('DEBUG', False))
    corr_id = get_corr_id_context_var_str()

    logger.debug('hello world')
    stdout = capsys.readouterr().out
    assert corr_id not in stdout

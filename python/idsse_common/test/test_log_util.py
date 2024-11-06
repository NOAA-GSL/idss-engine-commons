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
# pylint: disable=missing-class-docstring

import contextvars
import logging
import logging.config
import threading
import time
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


def test_getting_logs_from_threaded_func(capsys):
    logging.config.dictConfig(get_default_log_config('INFO', True))
    set_corr_id_context_var(EXAMPLE_ORIGINATOR, key=EXAMPLE_UUID)

    def worker():
        logger = logging.getLogger(__name__)
        logger.info(EXAMPLE_LOG_MESSAGE)

    # Create and start the thread
    thread = threading.Thread(target=contextvars.copy_context().run, args=(worker,))
    thread.start()

    time.sleep(.1)
    stdout = capsys.readouterr().out
    assert EXAMPLE_LOG_MESSAGE in stdout


def test_getting_logs_from_thread_class(capsys):
    logging.config.dictConfig(get_default_log_config('INFO', True))
    set_corr_id_context_var(EXAMPLE_ORIGINATOR, key=EXAMPLE_UUID)

    def set_context(context):
        for var, value in context.items():
            var.set(value)

    class MyThread(threading.Thread):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.context = contextvars.copy_context()

        def run(self):
            set_context(self.context)
            logger = logging.getLogger(f'{__name__}::{self.__class__.__name__}')
            logger.info(EXAMPLE_LOG_MESSAGE)

    thread = MyThread()
    thread.start()
    thread.join()

    stdout = capsys.readouterr().out
    assert EXAMPLE_LOG_MESSAGE in stdout

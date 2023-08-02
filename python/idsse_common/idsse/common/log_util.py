"""Module for providing the tools logging including the incorporation of correlation id"""
# ------------------------------------------------------------------------------
# Created on Thu Apr 27 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved.
#
# Contributors:
#     Geary Layne
#
# ------------------------------------------------------------------------------

import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Union

from .utils import to_iso

# flake8: noqa E501
# pylint: disable=line-too-long
# cSpell:words gmtime

# correlation_id: ContextVar[uuid.UUID] = \
#     ContextVar('correlation_id',
#                default=uuid.UUID('00000000-0000-0000-0000-000000000000'))
corr_id_context_var: ContextVar[str] = ContextVar('correlation_id')


def set_corr_id_context_var(originator: str, key: uuid = None, issue_dt: Union[str, datetime] = None) -> None:
    if not key:
        key = uuid.uuid4()

    if issue_dt:
        if not isinstance(issue_dt, str):
            issue_dt = to_iso(issue_dt)
        corr_id_context_var.set(f'{originator};{key};{issue_dt}')
    else:
        corr_id_context_var.set(f'{originator};{key};_')


def get_corr_id_context_var_str():
    return corr_id_context_var.get()

def get_corr_id_context_var_parts():
    return tuple([part for part in corr_id_context_var.get().split(';')])

class AddCorrelationIdFilter(logging.Filter):
    """"Provides correlation id parameter for the logger"""
    def filter(self, record):
        record.corr_id = corr_id_context_var.get()
        return True

class CorrIdFilter(logging.Filter):
    """"Provides correlation id parameter for the logger"""
    def __init__(self, corr_id, name: str = "") -> None:
        self._corr_id = corr_id
        super().__init__(name)

    def filter(self, record):
        return not hasattr(record, 'correlation_id') or self._corr_id == record.corr_id

class UTCFormatter(logging.Formatter):
    """"Provides a callable time format converter for the logging"""
    converter = time.gmtime


def get_default_log_config(level, with_corr_id=True):
    set_corr_id_context_var('None', uuid.UUID('00000000-0000-0000-0000-000000000000'))
    if with_corr_id:
        format_str = '%(asctime)-15s %(name)-5s %(levelname)-8s %(corr_id)s %(module)s::%(funcName)s(line %(lineno)d) %(message)s'
    else:
        format_str = '%(asctime)-15s %(name)-5s %(levelname)-8s %(module)s::%(funcName)s(line %(lineno)d) %(message)s'

    return {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            '()': UTCFormatter,
            'format': format_str
        },
    },
    'filters': {
        'corr_id': {
            '()': AddCorrelationIdFilter,
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'standard',
            'filters': ['corr_id', ],
        },
    },
    'loggers': {
        '': {
            'level': level,
            'handlers': ['default', ],
        },
    }
}

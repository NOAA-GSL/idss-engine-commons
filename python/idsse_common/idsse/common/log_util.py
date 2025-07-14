"""Module for providing the tools logging including the incorporation of correlation id"""

# ------------------------------------------------------------------------------
# Created on Thu Apr 27 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Geary Layne (1)
#     Mackenzie Grimes (2)
#
# ------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,missing-class-docstring

import logging
import time
import uuid
from collections.abc import Sequence
from contextvars import ContextVar
from datetime import datetime

from .utils import to_iso

# cSpell:words gmtime

corr_id_context_var: ContextVar[str] = ContextVar("correlation_id")


def set_corr_id_context_var(
    originator: str,
    key: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000000"),
    issue_dt: str | datetime | None = None,
) -> None:
    """
    Build and set correlation ID ContextVar for logging module, based on originator and
    key (or generated UUID). Include issue_dt in correlation ID if provided.

    Args:
        originator (str): Function, class, service name, etc. that is using logging module
        key (uuid.UUID, optional): a UUID. Default: randomly generated UUID.
        issue_dt (str | datetime | None, optional): Datetime when a relevant forecast was issued
    """
    if issue_dt:
        if not isinstance(issue_dt, str):
            issue_dt = to_iso(issue_dt)
        corr_id_context_var.set(f"{originator};{key};{issue_dt}")
    else:
        corr_id_context_var.set(f"{originator};{key};_")


def get_corr_id_context_var_str() -> str:
    """Getter for correlation ID ContextVar name"""
    return corr_id_context_var.get()


def get_corr_id_context_var_parts() -> Sequence[str]:
    """Split correlation ID ContextVar into its parts, such as [originator, key, issue_datetime]"""
    return corr_id_context_var.get().split(";")


class AddCorrelationIdFilter(logging.Filter):
    """Provides correlation id parameter for the logger"""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.corr_id = corr_id_context_var.get()
            return True
        except LookupError:  # couldn't add corr_id since it is not set
            return False


class CorrIdFilter(logging.Filter):
    """Provides correlation id parameter for the logger"""

    def __init__(self, corr_id, name: str = "") -> None:
        self._corr_id = corr_id
        super().__init__(name)

    def filter(self, record):
        return not hasattr(record, "correlation_id") or self._corr_id == record.corr_id


class UTCFormatter(logging.Formatter):
    """Provides a callable time format converter for the logging"""

    converter = time.gmtime


def get_default_log_config(
    level: str,
    with_corr_id: bool = True,
    host: str = "localhost",
    port: int = 5672,
    report_level: str = "ERROR",
):
    """
    Get standardized python logging config (formatters, handlers directing to stdout, rabbitmq etc.)
    as a dictionary. This dictionary can be passed directly to logging.config.dictConfig:

    import logging
    import logging.config

    logging.config.dictConfig(get_default_log_config('INFO'))
    logger = logging.getLogger(__name__)
    logger.info('hello world')

    Args:
        level (str): logging level, such as 'DEBUG'
        with_corr_id (bool): whether to include correlation ID in log messages. Default: True
        host (str): rabbitmq hostname
        port (int): rabbitmq port number
        report_level: rabbitmq logging level
    """
    set_corr_id_context_var("None", uuid.UUID("00000000-0000-0000-0000-000000000000"))
    if with_corr_id:
        format_str = (
            "%(asctime)-15s %(name)-5s %(levelname)-8s %(corr_id)s %(module)s::"
            "%(funcName)s (line %(lineno)d) %(message)s"
        )
        filter_list = [
            "corr_id",
        ]
    else:
        format_str = (
            "%(asctime)-15s %(name)-5s %(levelname)-8s %(module)s::"
            "%(funcName)s (line %(lineno)d) %(message)s"
        )
        filter_list = []

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"()": UTCFormatter, "format": format_str},
        },
        "filters": {
            "corr_id": {
                "()": AddCorrelationIdFilter,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "standard",
                "filters": filter_list,
            },
            "rabbit": {
                "class": "python_logging_rabbitmq.RabbitMQHandler",
                "host": host,
                "port": port,
                "formatter": "standard",
                "filters": filter_list,
                "level": report_level,
                "declare_exchange": True,
            },
        },
        "loggers": {
            "": {
                "level": level,
                "handlers": ["default"],  # , 'rabbit']
            },
        },
    }

"""Module for providing the tools to incorporate correlation id"""
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
import uuid
from contextvars import ContextVar


# correlation_id: ContextVar[uuid.UUID] = \
#     ContextVar('correlation_id',
#                default=uuid.UUID('00000000-0000-0000-0000-000000000000'))
correlation_id: ContextVar[str] = \
    ContextVar('correlation_id',
               default=f'None:{uuid.UUID("a0000000-0000-0000-0000-000000000000")}')


class AddCorrelationIdFilter(logging.Filter):
    """"Provides correlation id parameter for the logger"""
    def filter(self, record):
        record.correlation_id = correlation_id.get()
        return True

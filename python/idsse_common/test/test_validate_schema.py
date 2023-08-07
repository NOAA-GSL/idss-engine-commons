"""Test suite for validate_schema.py"""
# ----------------------------------------------------------------------------------
# Created on Fri Aug 04 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------

from datetime import datetime, timezone, timedelta


def to_iso(dt):
    # this almost works
    # dt.isoformat(timespec='milliseconds')
    return (f'{dt.strftime("%Y-%m-%dT%H:%M")}:{(dt.second + dt.microsecond / 1e6):.3f}'
            f'{"Z" if dt.tzinfo in [None, timezone.utc] else dt.strftime("%Z")[3:]}')


def test_validate_das_valid_request():
    request = {'sourceType': 'valid',
               'sourceObj': {'product': 'NBM.AWS.GRIB',
                             'region': 'CO',
                             'issueDt': '2022-01-02T12:00:00.000Z',
                             'field': 'TEMP'}}

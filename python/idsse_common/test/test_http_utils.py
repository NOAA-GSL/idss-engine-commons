"""Test suite for http_utils.py"""
# ----------------------------------------------------------------------------------
# Created on Tue Dec 3
#
# Copyright (c) 2023 Colorado State University. All rights reserved. (1)
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (2)
#
# Contributors:
#     Paul Hamer (1)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring,redefined-outer-name,pointless-statement
# pylint: disable=invalid-name,unused-argument

from datetime import datetime, timedelta, UTC

from pytest import fixture
from pytest_httpserver import HTTPServer

from idsse.common.http_utils import HttpUtils
from idsse.testing.utils.resources import get_resource_from_file


EXAMPLE_ISSUE = datetime(2024, 10, 30, 20, 54, 38, tzinfo=UTC)
EXAMPLE_VALID = datetime(2024, 10, 30, 20, 54, 38, tzinfo=UTC)

EXAMPLE_URL = 'http://127.0.0.1:5000/data/'
EXAMPLE_ENDPOINT = '3DRefl/MergedReflectivityQC_00.50'
EXAMPLE_PROD_DIR = '3DRefl/MergedReflectivityQC_00.50/'
EXAMPLE_FILES = ['MRMS_MergedReflectivityQC_00.50.latest.grib2.gz',
                 'MRMS_MergedReflectivityQC_00.50_20241030-205438.grib2.gz',
                 'MRMS_MergedReflectivityQC_00.50_20241030-205640.grib2.gz']
EXAMPLE_RETURN = get_resource_from_file('idsse.testing.idsse_common',
                                        'mrms_response.html')

# pylint: disable=duplicate-code, line-too-long


# fixtures
@fixture(scope="session")
def httpserver_listen_address():
    return "127.0.0.1", 5000

@fixture
def http_utils() -> HttpUtils:
    EXAMPLE_BASE_DIR = 'http://127.0.0.1:5000/data/'
    EXAMPLE_SUB_DIR = '3DRefl/MergedReflectivityQC_00.50/'
    EXAMPLE_FILE_BASE = ('MRMS_MergedReflectivityQC_00.50_{issue.year:04d}{issue.month:02d}{issue.day:02d}'
                         '-{issue.hour:02d}{issue.minute:02d}{issue.second:02d}')
    EXAMPLE_FILE_EXT = '.grib2.gz'

    return HttpUtils(EXAMPLE_BASE_DIR, EXAMPLE_SUB_DIR, EXAMPLE_FILE_BASE, EXAMPLE_FILE_EXT)


@fixture
def http_utils_with_wild() -> HttpUtils:
    EXAMPLE_BASE_DIR = 'http://127.0.0.1:5000/data/'
    EXAMPLE_SUB_DIR = '3DRefl/MergedReflectivityQC_00.50/'
    EXAMPLE_FILE_BASE = ('MRMS_MergedReflectivityQC_00.50_{issue.year:04d}{issue.month:02d}{issue.day:02d}'
                         '-{issue.hour:02d}{issue.minute:02d}?{issue.second:02d}')
    EXAMPLE_FILE_EXT = '.grib2.gz'

    return HttpUtils(EXAMPLE_BASE_DIR, EXAMPLE_SUB_DIR, EXAMPLE_FILE_BASE, EXAMPLE_FILE_EXT)

# test class methods
def test_get_path(http_utils: HttpUtils):
    result_path = http_utils.get_path(EXAMPLE_ISSUE, EXAMPLE_VALID)
    assert result_path == f'{EXAMPLE_URL}{EXAMPLE_PROD_DIR}MRMS_MergedReflectivityQC_00.50_20241030-205438.grib2.gz'


def test_http_ls(http_utils: HttpUtils, httpserver: HTTPServer):
    httpserver.expect_request('/data/'+EXAMPLE_ENDPOINT).respond_with_data(EXAMPLE_RETURN,
                                                                           content_type="text/plain")
    result = http_utils.http_ls(EXAMPLE_URL + EXAMPLE_ENDPOINT)
    assert len(result) == len(EXAMPLE_FILES)
    assert result[0] == f'{EXAMPLE_URL}{EXAMPLE_PROD_DIR}{EXAMPLE_FILES[0]}'


def test_http_ls_without_prepend_path(http_utils: HttpUtils, httpserver: HTTPServer):
    httpserver.expect_request('/data/'+EXAMPLE_ENDPOINT).respond_with_data(EXAMPLE_RETURN,
                                                                           content_type="text/plain")
    result = http_utils.http_ls(EXAMPLE_URL + EXAMPLE_ENDPOINT, prepend_path=False)
    assert len(result) == len(EXAMPLE_FILES)
    assert result[0] == EXAMPLE_FILES[0]


def test_http_ls_on_error(http_utils: HttpUtils, httpserver: HTTPServer):
    httpserver.expect_request('/data/'+EXAMPLE_ENDPOINT).respond_with_data('', content_type="text/plain")
    result = http_utils.http_ls(EXAMPLE_URL + EXAMPLE_ENDPOINT)
    assert result == []


def test_http_cp_succeeds(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_PROD_DIR+'/temp.grib2.gz'
    httpserver.expect_request(url).respond_with_data(bytes([0,1,2]), status=200,
                                                     content_type="application/octet-stream")
    path = f'{EXAMPLE_URL}{EXAMPLE_PROD_DIR}/temp.grib2.gz'
    dest = '/tmp/temp.grib2.gz'

    copy_success = http_utils.http_cp(path, dest)
    assert copy_success

def test_http_cp_fails(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_PROD_DIR+'/temp.grib2.gz'
    httpserver.expect_request(url).respond_with_data(bytes([0, 1, 2]), status=404,
                                                     content_type="application/octet-stream")
    path = f'{EXAMPLE_URL}{EXAMPLE_PROD_DIR}/temp.grib2.gz'
    dest = '/tmp/temp.grib2.gz'
    copy_success = http_utils.http_cp(path, dest)
    assert not copy_success


def test_check_for_succeeds(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_ENDPOINT
    httpserver.expect_request(url).respond_with_data(EXAMPLE_RETURN, content_type="text/plain")

    result = http_utils.check_for(EXAMPLE_ISSUE, EXAMPLE_VALID)
    assert result is not None
    assert result == (EXAMPLE_VALID, f'{EXAMPLE_URL}{EXAMPLE_PROD_DIR}{EXAMPLE_FILES[1]}')


def test_check_for_does_not_find_valid(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_ENDPOINT
    httpserver.expect_request(url).respond_with_data('', content_type="text/plain")
    unexpected_valid = datetime(1970, 10, 3, 23, tzinfo=UTC)
    result = http_utils.check_for(EXAMPLE_ISSUE, unexpected_valid)
    assert result is None


def test_get_issues(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/' + EXAMPLE_ENDPOINT +'/'
    httpserver.expect_request(url).respond_with_data(EXAMPLE_RETURN, content_type="text/plain")
    result = http_utils.get_issues(issue_start=EXAMPLE_ISSUE,
                                   time_delta=timedelta(minutes=1))
    assert len(result) == 1
    assert result[0] == EXAMPLE_ISSUE


def test_get_issues_with_same_start_stop(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_ENDPOINT+'/'
    httpserver.expect_request(url).respond_with_data(EXAMPLE_RETURN, content_type="text/plain")
    result = http_utils.get_issues(issue_start=EXAMPLE_ISSUE, issue_end=EXAMPLE_ISSUE, time_delta=timedelta(minutes=1))
    assert len(result) == 1
    assert result[0] == EXAMPLE_ISSUE

def test_get_valids_all(http_utils: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_ENDPOINT+'/'
    httpserver.expect_request(url).respond_with_data(EXAMPLE_RETURN, content_type="text/plain")
    result = http_utils.get_valids(EXAMPLE_ISSUE)
    assert len(result) == 0
    #assert result[0] == (EXAMPLE_VALID, f'{EXAMPLE_URL}{EXAMPLE_PROD_DIR}{EXAMPLE_FILES[1]}')


def test_get_valids_with_wildcards(http_utils_with_wild: HttpUtils, httpserver: HTTPServer):
    url = '/data/'+EXAMPLE_ENDPOINT+'/'
    httpserver.expect_request(url).respond_with_data(EXAMPLE_RETURN, content_type="text/plain")
    result = http_utils_with_wild.get_valids(EXAMPLE_ISSUE)
    assert len(result) == 0

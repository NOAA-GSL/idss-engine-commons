'''Module for testing the bit pack utils'''
# ----------------------------------------------------------------------------------
# Created on Fri Dec 15 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
# Copyright (c) 2023 Colorado State University. All rights reserved. (2)
#
# Contributors:
#     Geary Layne (1)
#     Paul Hamer (2)
#
# ----------------------------------------------------------------------------------
# pylint: disable=missing-function-docstring

import numpy
import pytest

from idsse.common.sci.bit_pack import (get_pack_info,
                                       get_min_max,
                                       pack_numpy_to_numpy,
                                       pack_numpy_to_list,
                                       pack_to_list,
                                       PackInfo,
                                       PackType)
def test_get_min_max():
    l = [-1.0, 0.0, 1.0, 2.0]
    expected = (-1.0, 2.0)
    res = get_min_max(l)
    assert res == expected
    a = numpy.array(l)
    res = get_min_max(a)
    assert res == expected


def test_get_pack_info_with_decimals():
    result = get_pack_info(-1, 1, decimals=2)
    expected = PackInfo(PackType.BYTE, 0.01, -1)
    assert result == expected


def test_get_pack_info_with_pack_type():
    result = get_pack_info(-1, 1, pack_type=PackType.SHORT)
    expected = PackInfo(PackType.SHORT, 3.0518043793392844e-05, -1)
    assert result.type == expected.type
    assert result.scale == pytest.approx(expected.scale)
    assert result.offset == expected.offset
    # Check for exceptions...
    with pytest.raises(ValueError):
        result = get_pack_info(-1, 1)
    with pytest.raises(ValueError):
        result = get_pack_info(-1, 1, decimals=2, pack_type=PackType.SHORT)

def test_pack_to_list():
    data = [[10, 50, 100, 200, 500], [30, 150, 300, 400, 600]]
    result = pack_to_list(data, in_place=False)
    expected = [[0, 4443, 9996, 21104, 54427], [2221, 15550, 32212, 43319, 65535]]
    numpy.testing.assert_array_equal(result.data, expected)
    assert data[0][0] != result.data[0][0]

    data = numpy.array(data, dtype=float)
    result = pack_to_list(data, in_place=False)
    expected = [[0, 4443, 9996, 21104, 54427], [2221, 15550, 32212, 43319, 65535]]
    numpy.testing.assert_array_equal(result.data, expected)
    assert data[0][0] != result.data[0][0]

    with pytest.raises(KeyError):
        result = pack_to_list((-1,1))

def test_pack_list_to_list():
    data = [[10, 50, 100, 200, 500], [30, 150, 300, 400, 600]]
    result = pack_to_list(data, in_place=False)
    expected = [[0, 4443, 9996, 21104, 54427], [2221, 15550, 32212, 43319, 65535]]
    numpy.testing.assert_array_equal(result.data, expected)
    assert data[0][0] != result.data[0][0]
    result = pack_to_list(data, in_place=True)

    with pytest.raises(KeyError):
        result = pack_to_list((-1,1))

def test_pack_numpy():
    data = numpy.array([[-1, -.5, 0, .5, 1], [-1, -.25, 0, .25, 1]])
    result = pack_numpy_to_numpy(data, in_place=False)
    expected = numpy.array([[0, 16383, 32767, 49151, 65535],
                            [0, 24575, 32767, 40959, 65535]])
    numpy.testing.assert_array_equal(result.data, expected)
    assert data[0, 0] != result.data[0, 0]

    with pytest.raises(ValueError):
        result = pack_numpy_to_numpy(numpy.array([0,1,2], dtype=int), in_place=True)

    with pytest.raises(ValueError):
        result = pack_numpy_to_numpy((-1,1))


def test_pack_numpy_in_place():
    data = numpy.array([[-100., -50, 0, 50, 100], [-100, 0, 100, 200, 300]])
    result = pack_numpy_to_numpy(data, in_place=True)
    expected = numpy.array([[0.,  8191., 16383., 24575., 32767.],
                            [0., 16383., 32767., 49151., 65535.]])
    numpy.testing.assert_array_equal(data, result.data, expected)
    assert data[0, 0] == result.data[0, 0]


def test_pack_numpy_to_list():
    data = numpy.array([[-1, -.5, 0, .5, 1], [-1, -.25, 0, .25, 1]])
    result = pack_numpy_to_list(data, decimals=2)
    expected = [[0, 50, 100, 150, 200],
                [0, 75, 100, 125, 200]]
    assert isinstance(result.data, list)
    assert isinstance(result.data[0][0], int)
    numpy.testing.assert_array_equal(result.data, expected)

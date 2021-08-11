#!/usr/bin/python

import argparse
import json
import os
from datetime import datetime
from enum import Enum

class DataRequest:

    def __init__(self, product, field, issueDt, validDt, label=None):
        self.dataRequest = {}
        data = {'product': product,
                'field': field,
                'issueDt': issueDt,
                'validDt': validDt}

        self._add_task('data', data, label)

    def _add_task(self, type, task, label):
        if self.dataRequest:
            task['source'] = self.dataRequest['source']
        source = {'sourceType': type,
                  'sourceObj': task}
        if label:
            source['label'] = label

        self.dataRequest['source'] = source
        return self

    def condition(self, relational, min, max, clip, thresh, secThresh=None, label=None):
        task = {
            'relational': relational,
            'thresh': thresh,
            'mapping': {
                'min': min,
                'max': max,
                'clip': clip,
            }
        }
        if secThresh:
            task['secThresh'] = secThresh

        return self._add_task('condition', task, label)

    def units(self, units, label=None):
        task = {
            'units': units
        }
        return self._add_task('units', task, label)

    def format(self, format, label=None):
        task = {
            'format': format
        }
        return self._add_task('format', task, label)

    def project(self, projSpec, gridSpec, method, label=None):
        task = {
            'projSpec': projSpec,
            'gridSpec': gridSpec,
            'method': method
        }
        return self._add_task('project', task, label)

    # join = 'cross' or 'zip'
    # indices = list (sized and ordered link source data) of either list of indexs or index builder simalar to slice notaion
    def slice(self, sliceParams, label=None):
        return self._add_task('slice', sliceParams, label)

    def permute(self, order, label=None):
        task = {
            'order': order,
        }
        return self._add_task('permute', task, label)

    def toJson(self):
        return json.dumps(self.dataRequest)

class ConditionJoin(DataRequest):
    def __init__(self, type, sources, label=None):
        self.dataRequest = {}
        task = {'type': type,
                'sources': [source.dataRequest['source'] for source in sources]}
        source = {'sourceType': 'conditionJoin',
                  'sourceObj': task}
        if label:
            source['label'] = label

        self.dataRequest['source'] = source

    def toJson(self):
        return json.dumps(self.dataRequest)

def nbmTemp():

    sliceD1 = {'dim': 1,
               'indices': '5,6,7,6,5,4'}
    sliceD2 = {'dim': 2,
               'indices': '1,2,3,5,8,13'}
    sliceD3 = {'dim': 3,
               'indices': '10:200'}
    sliceParams = {'join': 'cross',
                   'dims': [
                       {'join': 'zip',
                        'dims': [
                            sliceD1,
                            sliceD2
                        ]},
                       sliceD3
                   ]}
    issueDt = '2021/8/1 2'
    validDt = '2021/8/1 5'
    product = 'NBM'
    field = 'TEMP'
    units = 'DEG F'
    relational = 'LTE'
    thresh = 32
    min = 22
    max = 42
    clip = True

    raw_label = f'{product}_{field}_{units}'
    condition_label = f'{product}_{field}_{relational}_{thresh}_{units}'
    tempCondition = DataRequest(product, field, issueDt, validDt) \
                        .permute([1,0]) \
                        .slice(sliceParams) \
                        .units(units, raw_label) \
                        .condition(relational, min, max, clip,
                                   thresh, label=condition_label)

    field = 'WIND SPEED'
    units = 'MPH'
    relational = 'GT'
    thresh = 10
    min = 0
    max = 20
    clip = True
    raw_label = f'{product}_{field}_{units}'
    condition_label = f'{product}_{field}_{relational}_{thresh}_{units}'
    windCondition = DataRequest(product, field, issueDt, validDt) \
                        .units(units, raw_label) \
                        .condition(relational, min, max, clip,
                                   thresh, label=condition_label)

    relational = 'GTE'
    thresh = 40
    min = 0
    max = 60
    clip = True
    raw_label = f'{product}_{field}_{units}'
    condition_label = f'{product}_{field}_{relational}_{thresh}_{units}'
    highWindCondition = DataRequest(product, field, issueDt, validDt) \
                        .units(units, raw_label) \
                        .condition(relational, min, max, clip,
                                   thresh, label=condition_label)

    # print(tempCondition)
    print(tempCondition.toJson())
    # print(windCondition)
    print(windCondition.toJson())
    print(highWindCondition.toJson())

    tempAndWindCondition = ConditionJoin('AND', [tempCondition, windCondition])

    print(tempAndWindCondition.toJson())

    orCondition = ConditionJoin('OR', [tempAndWindCondition, highWindCondition]).format("Netcdf")

    print(orCondition.toJson())



if "__main__" == __name__:
    nbmTemp()

    # def parse_slice(value):
    #     """
    #     Parses a `slice()` from string, like `start:stop:step`.
    #     """
    #     if value:
    #         parts = value.split(':')
    #         if len(parts) == 1:
    #             # slice(stop)
    #             parts = [None, parts[0]]
    #         # else: slice(start, stop[, step])
    #     else:
    #         # slice()
    #         parts = []
    #     return slice(*[int(p) if p else None for p in parts])
    #
    #
    # # unit tests:
    # try:
    #     assert parse_slice('')
    #     assert False, 'It should raise TypeError'
    # except TypeError:
    #     pass
    # assert parse_slice('2') == slice(2)
    # assert parse_slice('2:3') == slice(2, 3)
    # assert parse_slice(':3') == slice(None, 3)
    # assert parse_slice(':') == slice(None, None)
    # assert parse_slice('2:') == slice(2, None)
    # assert parse_slice('2:3:4') == slice(2, 3, 4)
    # assert parse_slice(':3:4') == slice(None, 3, 4)
    # assert parse_slice('2::4') == slice(2, None, 4)
    # assert parse_slice('2:3:') == slice(2, 3, None)
    # assert parse_slice('::4') == slice(None, None, 4)
    # assert parse_slice('2::') == slice(2, None, None)
    # assert parse_slice('::') == slice(None, None, None)
    # assert parse_slice('-12:-13:-14') == slice(-12, -13, -14)
    # assert parse_slice('2:3:-4') == slice(2, 3, -4)
    # try:
    #     parse_slice('1:2:3:4')
    #     assert False, 'It should raise TypeError'
    # except TypeError:
    #     pass
    #
    # x = [1,2,3,4,5,6]
    # import numpy
    # x = numpy.array(x)
    #
    # print(x[slice(2)])
    # print(x[[2,3,5]])
    # print(x[parse_slice(value=None)])
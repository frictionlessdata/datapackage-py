 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from datapackage import infer


# Tests

def test_infer():
    descriptor = infer('datapackage/*.csv', base_path='data')
    assert descriptor == {
        'profile': 'tabular-data-package',
        'resources': [{'encoding': 'utf-8',
            'format': 'csv',
            'mediatype': 'text/csv',
            'name': 'data',
            'path': 'datapackage/data.csv',
            'profile': 'tabular-data-resource',
            'schema': {'fields': [
                {'format': 'default', 'name': 'id', 'type': 'integer'},
                {'format': 'default', 'name': 'city', 'type': 'string'}],
                'missingValues': ['']}}]}


def test_infer_non_utf8_file():
    descriptor = infer('data/data_with_accents.csv')
    assert descriptor['resources'][0]['encoding'] == 'windows-1252'

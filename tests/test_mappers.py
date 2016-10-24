# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from importlib import import_module
module = import_module('datapackage.mappers')


# Tests

def test_convert_path():
    assert module.convert_path('path.csv', 'name') == 'path___name'
    assert module.convert_path('dir/path.csv', 'name') == 'dir__path___name'
    assert module.convert_path('path.csv', 'Some Name') == 'path___some_name'


def test_restore_path():
    assert module.restore_path('path___name') == ('path.csv', 'name')
    assert module.restore_path('dir__path___name') == ('dir/path.csv', 'name')
    assert module.restore_path('path___some_name') == ('path.csv', 'some_name')


def test_convert_schemas_self_reference():
    mapping = {}
    schema = {'foreignKeys': [{'reference': {'resource': 'self'}}]}
    result = module.convert_schemas(mapping, [schema])
    assert result[0] == schema


def test_convert_schemas_resource_reference():
    mapping = {'resource_name': 'table_name'}
    schema = {'foreignKeys': [{'reference': {'resource': 'resource_name'}}]}
    result = module.convert_schemas(mapping, [schema])
    assert result[0] == {'foreignKeys': [{'reference': {'resource': 'table_name'}}]}


def test_convert_schemas_resource_missing():
    mapping = {}
    schema = {'foreignKeys': [{'reference': {'resource': 'resource_name'}}]}
    with pytest.raises(ValueError):
        module.convert_schemas(mapping, [schema])


def test_restore_resources():
    resource = {'schema': {'foreignKeys': [{'reference': {'resource':  'path___name'}}]}}
    result = module.restore_resources([resource])
    assert result[0] == {'schema': {'foreignKeys': [{'reference': {'resource': 'name'}}]}}

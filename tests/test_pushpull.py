# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import mock
import pytest
import shutil
import tempfile
from mock import patch, ANY
from datapackage import DataPackage
from datapackage import helpers
from importlib import import_module
from tests import test_helpers
module = import_module('datapackage.pushpull')


# Tests

def test_push_datapackage(storage):

    # Prepare and call
    descriptor = test_helpers.fixture_path('datapackage', 'datapackage.json')
    storage.buckets = ['data___data']  # Without patch it's a reflection
    module.push_datapackage(descriptor=descriptor, backend='backend')

    # Assert mocked calls
    storage.create.assert_called_with(
        ['data___data'],
        [{'fields': [
            {'name': 'id', 'type': 'integer', 'format': 'default'},
            {'name': 'city', 'type': 'string', 'format': 'default'}],
          'missingValues': ['']}])
    storage.write.assert_called_with('data___data', ANY)

    # Assert writen data
    data = storage.write.call_args[0][1]
    assert list(data) == [
        (1, 'London'),
        (2, 'Paris'),
    ]


def test_pull_datapackage(storage, descriptor):

    # Prepare and call
    storage.buckets = ['data___data']
    storage.describe.return_value = (
        {'fields': [
            {'name': 'id', 'type': 'integer'},
            {'name': 'city', 'type': 'string'}]})
    storage.read.return_value = [
        (1, 'London'),
        (2, 'Paris'),
    ]
    module.pull_datapackage(descriptor=descriptor, name='name', backend='backend')

    # Assert pulled datapackage
    dp = DataPackage(descriptor)
    assert dp.descriptor == helpers.expand_data_package_descriptor(
        {'name': 'name',
        'resources': [
            {'path': ['data.csv'],
             'name': 'data',
             'schema':
                {'fields': [
                    {'name': 'id', 'type': 'integer'},
                    {'name': 'city', 'type': 'string'}]}}]})


def test_convert_path():
    assert module._convert_path('path.csv', 'name') == 'path___name'
    assert module._convert_path('dir/path.csv', 'name') == 'dir__path___name'
    assert module._convert_path('path.csv', 'Some Name') == 'path___some_name'


def test_restore_path():
    assert module._restore_path('path___name') == ('path.csv', 'name')
    assert module._restore_path('dir__path___name') == ('dir/path.csv', 'name')
    assert module._restore_path('path___some_name') == ('path.csv', 'some_name')


def test_convert_schemas_self_reference():
    mapping = {}
    schema = {'foreignKeys': [{'reference': {'resource': 'self'}}]}
    result = module._convert_schemas(mapping, [schema])
    assert result[0] == schema


def test_convert_schemas_resource_reference():
    mapping = {'resource_name': 'table_name'}
    schema = {'foreignKeys': [{'reference': {'resource': 'resource_name'}}]}
    result = module._convert_schemas(mapping, [schema])
    assert result[0] == {'foreignKeys': [{'reference': {'resource': 'table_name'}}]}


def test_convert_schemas_resource_missing():
    mapping = {}
    schema = {'foreignKeys': [{'reference': {'resource': 'resource_name'}}]}
    with pytest.raises(ValueError):
        module._convert_schemas(mapping, [schema])


def test_restore_resources():
    resource = {'schema': {'foreignKeys': [{'reference': {'resource':  'path___name'}}]}}
    result = module._restore_resources([resource])
    assert result[0] == {'schema': {'foreignKeys': [{'reference': {'resource': 'name'}}]}}


# Fixtures

@pytest.fixture
def storage(request):
    import_module = patch.object(module, 'import_module').start()
    storage = import_module.return_value.Storage.return_value
    request.addfinalizer(patch.stopall)
    return storage


@pytest.fixture
def descriptor(request):
    basedir = tempfile.mkdtemp()
    descriptor = os.path.join(basedir, 'datapackage.json')
    def delete():
        shutil.rmtree(basedir)
    request.addfinalizer(delete)
    return descriptor

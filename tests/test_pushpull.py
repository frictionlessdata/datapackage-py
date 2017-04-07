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
import tests.test_helpers as helpers
from mock import patch, ANY
from datapackage import DataPackage
from importlib import import_module
module = import_module('datapackage.pushpull')


# Tests

def test_push_datapackage(storage):

    # Prepare and call
    descriptor = helpers.fixture_path('datapackage', 'datapackage.json')
    storage.buckets = ['data___data']  # Without patch it's a reflection
    module.push_datapackage(descriptor=descriptor, backend='backend')

    # Assert mocked calls
    storage.create.assert_called_with(
        ['data___data'],
        [{'fields': [
            {'name': 'id', 'type': 'integer'},
            {'name': 'city', 'type': 'string'}]}])
    storage.write.assert_called_with('data___data', ANY)

    # Assert writen data
    data = storage.write.call_args[0][1]
    assert list(data) == [
        (1, 'London'),
        (2, 'Paris'),
    ]


@mock.patch('datapackage.helpers.expand_data_package_descriptor')
def test_pull_datapackage(_, storage, descriptor):

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
    assert dp.descriptor == {'name': 'name', 'resources': [
        {'path': 'data.csv', 'name': 'data', 'schema':
            {'fields': [
                {'name': 'id', 'type': 'integer'},
                {'name': 'city', 'type': 'string'}]}}]}


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

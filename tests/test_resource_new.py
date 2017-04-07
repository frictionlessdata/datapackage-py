 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import pytest
import httpretty
from functools import partial
from datapackage.resource_new import Resource
from datapackage.helpers import expand_resource_descriptor as expand
from datapackage import exceptions


# Resource.descriptor (retrieve)

def test_descriptor_retrieve_dict():
    descriptor = {
        'name': 'name',
        'data': 'data',
    }
    actual = Resource(descriptor).descriptor
    expect = expand(descriptor)
    assert actual == expect


def test_descriptor_retrieve_path():
    descriptor = 'tests/fixtures/data-resource.json'
    actual = Resource(descriptor).descriptor
    expect = expand(json.load(io.open(descriptor, encoding='utf-8')))
    assert actual == expect


def test_descriptor_retrieve_path_bad():
    descriptor = 'tests/fixtures/bad-path.json'
    with pytest.raises(exceptions.DataPackageException):
        Resource(descriptor).descriptor


@httpretty.activate
def test_descriptor_retrieve_url(patch_get):
    descriptor = 'http://example.com/descriptor.json'
    descriptor_contents = {
        'name': 'name',
        'data': 'data',
    }
    # Mocks
    patch_get(descriptor, body=json.dumps(descriptor_contents))
    # Tests
    actual = Resource(descriptor).descriptor
    expect = expand(descriptor_contents)
    assert actual == expect


@httpretty.activate
def test_descriptor_retrieve_url_bad(patch_get):
    descriptor = 'http://example.com/descriptor.json'
    # Mocks
    patch_get(descriptor, status=500)
    # Tests
    with pytest.raises(exceptions.DataPackageException):
        Resource(descriptor).descriptor


# Resource.descriptor (dereference)

def test_descriptor_dereference():
    descriptor = 'tests/fixtures/resource_with_dereferencing.json'
    resource = Resource(descriptor)
    assert resource.descriptor == expand({
        'name': 'name',
        'data': 'data',
        'schema': {'fields': [{'name': 'name'}]},
        'dialect': {'delimiter': ','},
        'dialects': {'main': {'delimiter': ','}},
    })


def test_descriptor_dereference_pointer():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': '#/schemas/main',
        'schemas': {'main': {'fields': [{'name': 'name'}]}},
    }
    resource = Resource(descriptor)
    assert resource.descriptor == expand({
        'name': 'name',
        'data': 'data',
        'schema': {'fields': [{'name': 'name'}]},
        'schemas': {'main': {'fields': [{'name': 'name'}]}},
    })


def test_descriptor_dereference_pointer_bad():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': '#/schemas/main',
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor)


@httpretty.activate
def test_descriptor_dereference_remote(patch_get):
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': 'http://example.com/schema',
    }
    # Mocks
    patch_get('http://example.com/schema', body='{"fields": [{"name": "name"}]}')
    # Tests
    resource = Resource(descriptor)
    assert resource.descriptor == expand({
        'name': 'name',
        'data': 'data',
        'schema': {'fields': [{'name': 'name'}]},
    })


@httpretty.activate
def test_descriptor_dereference_remote_bad(patch_get):
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': 'http://example.com/schema',
    }
    # Mocks
    patch_get('http://example.com/schema', status=404)
    # Tests
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor)


def test_descriptor_dereference_local():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': 'table_schema.json',
    }
    resource = Resource(descriptor, base_path='tests/fixtures')
    assert resource.descriptor == expand({
        'name': 'name',
        'data': 'data',
        'schema': {'fields': [{'name': 'name'}]},
    })


def test_descriptor_dereference_local_bad():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': 'bad_path.json',
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='tests/fixtures')


def test_descriptor_dereference_local_bad_not_safe():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': '../fixtures/table_schema.json',
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='tests/fixtures')


# Resource.descriptor (expand)

def test_descriptor_expand():
    descriptor = {
        'name': 'name',
        'data': 'data',
    }
    resource = Resource(descriptor)
    assert resource.descriptor == {
        'name': 'name',
        'data': 'data',
        'profile': 'data-resource',
        'encoding': 'utf-8',
    }


def test_descriptor_expand_tabular_schema():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'profile': 'tabular-data-resource',
        'schema': {
            'fields': [{'name': 'name'}],
        },
    }
    resource = Resource(descriptor)
    assert resource.descriptor == {
        'name': 'name',
        'data': 'data',
        'profile': 'tabular-data-resource',
        'encoding': 'utf-8',
        'schema': {
            'fields': [{'name': 'name', 'type': 'string', 'format': 'default'}],
            'missingValues': [''],
        }
    }


def test_descriptor_expand_tabular_dialect():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'profile': 'tabular-data-resource',
        'dialect': {
            'delimiter': 'custom',
        }
    }
    resource = Resource(descriptor)
    assert resource.descriptor == {
        'name': 'name',
        'data': 'data',
        'profile': 'tabular-data-resource',
        'encoding': 'utf-8',
        'dialect': {
            'delimiter': 'custom',
            'doubleQuote': True,
            'lineTerminator': '\r\n',
            'quoteChar': '""',
            'escapeChar': '\\',
            'skipInitialSpace': True,
            'header': True,
            'caseSensitiveHeader': False,
        }
    }


# Resource.type/source

def test_source_inline():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'path': ['path'],
    }
    resource = Resource(descriptor)
    assert resource.source == 'data'
    assert resource.source_type == 'inline'


def test_source_local():
    descriptor = {
        'name': 'name',
        'path': ['table.csv'],
    }
    resource = Resource(descriptor, base_path='tests/fixtures')
    assert resource.source == 'tests/fixtures/table.csv'
    assert resource.source_type == 'local'


def test_source_local_bad_no_base_path():
    descriptor = {
        'name': 'name',
        'path': ['table.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor)


def test_source_local_bad_not_safe_absolute():
    descriptor = {
        'name': 'name',
        'path': ['/fixtures/table.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='tests/fixtures')


def test_source_local_bad_not_safe_traversing():
    descriptor = {
        'name': 'name',
        'path': ['../fixtures/table.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='tests/fixtures')


def test_source_remote():
    descriptor = {
        'name': 'name',
        'path': ['http://example.com/table.csv'],
    }
    resource = Resource(descriptor)
    assert resource.source == 'http://example.com/table.csv'
    assert resource.source_type == 'remote'


def test_source_remote_path_relative_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['table.csv'],
    }
    resource = Resource(descriptor, base_path='http://example.com/')
    assert resource.source == 'http://example.com/table.csv'
    assert resource.source_type == 'remote'


def test_source_remote_path_remote_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['http://example1.com/table.csv'],
    }
    resource = Resource(descriptor, base_path='http://example2.com/')
    assert resource.source == 'http://example1.com/table.csv'
    assert resource.source_type == 'remote'


def test_source_multipart_local():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'chunk2.csv'],
    }
    resource = Resource(descriptor, base_path='tests/fixtures')
    assert resource.source == ['tests/fixtures/chunk1.csv', 'tests/fixtures/chunk2.csv']
    assert resource.source_type == 'multipart-local'


def test_source_multipart_local_bad_no_base_path():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'chunk2.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor)


def test_source_multipart_local_bad_not_safe_absolute():
    descriptor = {
        'name': 'name',
        'path': ['/fixtures/chunk1.csv', 'chunk2.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='tests/fixtures')


def test_source_multipart_local_bad_not_safe_traversing():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', '../fixtures/chunk2.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='tests/fixtures')


def test_source_multipart_remote():
    descriptor = {
        'name': 'name',
        'path': ['http://example.com/chunk1.csv', 'http://example.com/chunk2.csv'],
    }
    resource = Resource(descriptor)
    assert resource.source == [
        'http://example.com/chunk1.csv', 'http://example.com/chunk2.csv']
    assert resource.source_type == 'multipart-remote'


def test_source_multipart_remote_path_relative_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'chunk2.csv'],
    }
    resource = Resource(descriptor, base_path='http://example.com')
    assert resource.source == [
        'http://example.com/chunk1.csv', 'http://example.com/chunk2.csv']
    assert resource.source_type == 'multipart-remote'


def test_source_multipart_remote_path_remote_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'http://example2.com/chunk2.csv'],
    }
    resource = Resource(descriptor, base_path='http://example1.com')
    assert resource.source == [
        'http://example1.com/chunk1.csv', 'http://example2.com/chunk2.csv']
    assert resource.source_type == 'multipart-remote'


# Resource.table

def test_descriptor_table():
    descriptor = {
        'name': 'name',
        'data': 'data',
    }
    resource = Resource(descriptor)
    assert resource.table is None


def test_descriptor_table_tabular_inline():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'data': [
            ['id', 'name'],
            ['1', 'english'],
            ['2', '中国人'],
        ],
        'schema': 'resource_schema.json',
    }
    resource = Resource(descriptor, base_path='tests/fixtures')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


def test_descriptor_table_tabular_local():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['resource_data.csv'],
        'schema': 'resource_schema.json',
    }
    resource = Resource(descriptor, base_path='tests/fixtures')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


@httpretty.activate
def test_descriptor_table_tabular_remote(patch_get):
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['http://example.com/resource_data.csv'],
        'schema': 'resource_schema.json',
    }
    # Mocks
    patch_get('http://example.com/resource_data.csv',
        body="id,name\n1,english\n2,中国人")
    # Tests
    resource = Resource(descriptor, base_path='tests/fixtures')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


# Helpers

@pytest.fixture
def patch_get():
    return partial(httpretty.register_uri, httpretty.GET)

 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import pytest
import httpretty
from copy import deepcopy
from mock import Mock, ANY
from functools import partial
from tableschema import Storage
from datapackage.resource import Resource
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
    descriptor = 'data/data-resource.json'
    actual = Resource(descriptor).descriptor
    expect = expand(json.load(io.open(descriptor, encoding='utf-8')))
    assert actual == expect


def test_descriptor_retrieve_path_bad():
    descriptor = 'data/bad-path.json'
    with pytest.raises(exceptions.DataPackageException):
        Resource(descriptor).descriptor


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


def test_descriptor_retrieve_url_bad(patch_get):
    descriptor = 'http://example.com/descriptor.json'
    # Mocks
    patch_get(descriptor, status=500)
    # Tests
    with pytest.raises(exceptions.DataPackageException):
        Resource(descriptor).descriptor


# Resource.descriptor (dereference)

def test_descriptor_dereference():
    descriptor = 'data/resource_with_dereferencing.json'
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
    resource = Resource(descriptor, base_path='data')
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
        resource = Resource(descriptor, base_path='data')


def test_descriptor_dereference_local_bad_not_safe():
    descriptor = {
        'name': 'name',
        'data': 'data',
        'schema': '../fixtures/table_schema.json',
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='data')


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
        'dialect': {
            'delimiter': 'custom',
            'doubleQuote': True,
            'lineTerminator': '\r\n',
            'quoteChar': '"',
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
    assert resource.inline == True


def test_source_local():
    descriptor = {
        'name': 'name',
        'path': ['table.csv'],
    }
    resource = Resource(descriptor, base_path='data')
    assert resource.source == 'data/table.csv'
    assert resource.local == True


def test_source_local_bad_no_base_path():
    descriptor = {
        'name': 'name',
        'path': ['table.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='')


def test_source_local_bad_not_safe_absolute():
    descriptor = {
        'name': 'name',
        'path': ['/fixtures/table.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='data')


def test_source_local_bad_not_safe_traversing():
    descriptor = {
        'name': 'name',
        'path': ['../fixtures/table.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='data')


def test_source_remote():
    descriptor = {
        'name': 'name',
        'path': ['http://example.com/table.csv'],
    }
    resource = Resource(descriptor)
    assert resource.source == 'http://example.com/table.csv'
    assert resource.remote == True


def test_source_remote_path_relative_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['table.csv'],
    }
    resource = Resource(descriptor, base_path='http://example.com/')
    assert resource.source == 'http://example.com/table.csv'
    assert resource.remote == True


def test_source_remote_path_remote_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['http://example1.com/table.csv'],
    }
    resource = Resource(descriptor, base_path='http://example2.com/')
    assert resource.source == 'http://example1.com/table.csv'
    assert resource.remote == True


def test_source_multipart_local():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'chunk2.csv'],
    }
    resource = Resource(descriptor, base_path='data')
    assert resource.source == ['data/chunk1.csv', 'data/chunk2.csv']
    assert resource.local == True
    assert resource.multipart == True


def test_source_multipart_local_bad_no_base_path():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'chunk2.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='')


def test_source_multipart_local_bad_not_safe_absolute():
    descriptor = {
        'name': 'name',
        'path': ['/fixtures/chunk1.csv', 'chunk2.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='data')


def test_source_multipart_local_bad_not_safe_traversing():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', '../fixtures/chunk2.csv'],
    }
    with pytest.raises(exceptions.DataPackageException):
        resource = Resource(descriptor, base_path='data')


def test_source_multipart_remote():
    descriptor = {
        'name': 'name',
        'path': ['http://example.com/chunk1.csv', 'http://example.com/chunk2.csv'],
    }
    resource = Resource(descriptor)
    assert resource.source == [
        'http://example.com/chunk1.csv', 'http://example.com/chunk2.csv']
    assert resource.remote == True
    assert resource.multipart == True


def test_source_multipart_remote_path_relative_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'chunk2.csv'],
    }
    resource = Resource(descriptor, base_path='http://example.com')
    assert resource.source == [
        'http://example.com/chunk1.csv', 'http://example.com/chunk2.csv']
    assert resource.remote == True
    assert resource.multipart == True


def test_source_multipart_remote_path_remote_and_base_path_remote():
    descriptor = {
        'name': 'name',
        'path': ['chunk1.csv', 'http://example2.com/chunk2.csv'],
    }
    resource = Resource(descriptor, base_path='http://example1.com')
    assert resource.source == [
        'http://example1.com/chunk1.csv', 'http://example2.com/chunk2.csv']
    assert resource.remote == True
    assert resource.multipart == True


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
    resource = Resource(descriptor, base_path='data')
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
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


def test_descriptor_table_tabular_remote(patch_get):
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['http://example.com/resource_data.csv'],
        'schema': 'resource_schema.json',
    }
    # Mocks
    patch_get('http://example.com/resource_data.csv', body="id,name\n1,english\n2,中国人")
    # Tests
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


def test_descriptor_table_tabular_multipart_local():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['chunk1.csv', 'chunk2.csv'],
        'schema': 'resource_schema.json',
    }
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


def test_descriptor_table_tabular_multipart_remote(patch_get):
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': [
            'http://example.com/chunk1.csv',
            'http://example.com/chunk2.csv',
            'http://example.com/chunk3.csv',
        ],
        'schema': 'resource_schema.json',
    }
    # Mocks
    patch_get('http://example.com/chunk1.csv', body="id,name\n")
    patch_get('http://example.com/chunk2.csv', body="1,english")
    patch_get('http://example.com/chunk3.csv', body="2,中国人\n")
    # Tests
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


def test_descriptor_table_tabular_skip_rows():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['resource_data.csv'],
        'schema': 'resource_schema.json',
        'skipRows': [2],
    }
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 2, 'name': '中国人'},
    ]


def test_resource_options_skip_rows():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['resource_data.csv'],
        'schema': 'resource_schema.json',
    }
    resource = Resource(descriptor, base_path='data', skip_rows=[2])
    assert resource.table.read(keyed=True) == [
        {'id': 2, 'name': '中国人'},
    ]


def test_descriptor_table_tabular_dialect_custom():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['dialect.csv'],
        'schema': 'resource_schema.json',
        'dialect': {
            'delimiter': '|',
            'quoteChar': '#',
            'escapeChar': '-',
            'doubleQuote': False,
            'skipInitialSpace': False,
        },
    }
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': ' |##'},
    ]


def test_descriptor_table_tabular_dialect_header_false():
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['chunk2.csv'],
        'schema': 'resource_schema.json',
        'dialect': {'header': False},
    }
    resource = Resource(descriptor, base_path='data')
    assert resource.table.read(keyed=True) == [
        {'id': 2, 'name': '中国人'},
    ]

# Resource table options
def test_resource_table_options(patch_get):
    descriptor = {
        'name': 'name',
        'profile': 'tabular-data-resource',
        'path': ['http://example.com/resource_data.csv'],
        'schema': 'resource_schema.json',
    }
    # Mocks
    patch_get('http://example.com/resource_data.csv', body="\n\nid,name\n1,english\n2,中国人")
    # Tests
    resource = Resource(descriptor, base_path='data', headers=3)
    assert resource.table.read(keyed=True) == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]


# Resource.raw_iter/read

def test_raw_iter():
    resource = Resource({'path': 'data/foo.txt'})
    with resource.raw_iter() as filelike:
        assert list(filelike) == [b'foo\n']


def test_raw_read():
    resource = Resource({'path': 'data/foo.txt'})
    assert resource.raw_read() == b'foo\n'


# Storage

def test_load_data_from_storage():
    SCHEMA = {
        'fields': [{'format': 'default', 'name': 'id', 'type': 'integer'}],
        'missingValues': ['']
    }
    storage = Mock(
        buckets=['data'],
        describe=lambda bucket: {'fields': [{'name': 'id', 'type': 'integer'}]},
        iter=lambda bucket: [[1], [2], [3]],
        spec=Storage)
    resource = Resource({'path': 'data'}, storage=storage)
    resource.infer(confidence=0.8)
    assert resource.descriptor == {
        'name': 'data',
        'path': 'data',
        'profile': 'tabular-data-resource',
        'schema': SCHEMA}
    assert resource.headers == ['id']
    assert resource.read() == [[1], [2], [3]]


def test_save_data_to_storage():
    SCHEMA = {
        'fields': [{'format': 'default', 'name': 'id', 'type': 'integer'}],
        'missingValues': ['']
    }
    storage = Mock(spec=Storage)
    resource = Resource({'data': [['id'], [1], [2], [3]]})
    resource.save('data', storage=storage)
    storage.create.assert_called_with('data', SCHEMA, force=True)
    storage.write.assert_called_with('data', ANY)


# TODO: use a self-removing directory
def test_save_data_to_json():
    resource = Resource({'data': [['id'], [1], [2], [3]]})
    resource.save('tmp/data.json')
    with open('tmp/data.json', 'r') as test_file:
        assert json.loads(test_file.read()) == {'data': [['id'], [1], [2], [3]], 'profile': 'data-resource'}


# TODO: use a self-removing directory
def test_save_data_to_json_base_path():
    resource = Resource({'data': [['id'], [1], [2], [3]]}, base_path='tmp')
    resource.save('data.json', to_base_path=True)
    with open('tmp/data.json', 'r') as test_file:
        assert json.loads(test_file.read()) == {'data': [['id'], [1], [2], [3]], 'profile': 'data-resource'}


# Integrity

DESCRIPTOR = {
    'name': 'data.csv',
    'path': 'data/data.csv',
    'bytes': 63,
    'hash': 'sha256:328adab247692a1a405e83c2625d52e366389eabf8a1824931187877e8644774',
}

def test_read_integrity():
    descriptor = deepcopy(DESCRIPTOR)
    resource = Resource(descriptor)
    resource.read(integrity=True)
    assert True


def test_read_integrity_error():
    descriptor = deepcopy(DESCRIPTOR)
    descriptor['bytes'] += 1
    descriptor['hash'] += 'a'
    resource = Resource(descriptor)
    with pytest.raises(exceptions.IntegrityError) as excinfo:
        resource.read(integrity=True)
    assert str(DESCRIPTOR['bytes']) in str(excinfo.value)
    assert DESCRIPTOR['hash'].replace('sha256:', '') in str(excinfo.value)


def test_read_integrity_size():
    descriptor = deepcopy(DESCRIPTOR)
    descriptor['hash'] = None
    resource = Resource(descriptor)
    resource.read(integrity=True)
    assert True


def test_read_integrity_size_error():
    descriptor = deepcopy(DESCRIPTOR)
    descriptor['bytes'] += 1
    descriptor['hash'] = None
    resource = Resource(descriptor)
    with pytest.raises(exceptions.IntegrityError) as excinfo:
        resource.read(integrity=True)
    assert str(DESCRIPTOR['bytes']) in str(excinfo.value)


def test_read_integrity_hash():
    descriptor = deepcopy(DESCRIPTOR)
    descriptor['bytes'] = None
    resource = Resource(descriptor)
    resource.read(integrity=True)
    assert True


def test_read_integrity_hash_error():
    descriptor = deepcopy(DESCRIPTOR)
    descriptor['bytes'] = None
    descriptor['hash'] += 'a'
    resource = Resource(descriptor)
    with pytest.raises(exceptions.IntegrityError) as excinfo:
        resource.read(integrity=True)
    assert DESCRIPTOR['hash'].replace('sha256:', '') in str(excinfo.value)


def test_check_integrity():
    descriptor = deepcopy(DESCRIPTOR)
    resource = Resource(descriptor)
    assert resource.check_integrity()


def test_check_integrity_error():
    descriptor = deepcopy(DESCRIPTOR)
    descriptor['bytes'] += 1
    descriptor['hash'] += 'a'
    resource = Resource(descriptor)
    with pytest.raises(exceptions.IntegrityError) as excinfo:
        resource.check_integrity()
    assert str(DESCRIPTOR['bytes']) in str(excinfo.value)
    assert DESCRIPTOR['hash'].replace('sha256:', '') in str(excinfo.value)


# Deprecated

def test_data():
    resource = Resource({'path': 'data/cities.tsv'})
    assert resource.data[0:3] == [
        {'Area': '1807.92', 'Name': 'Acrelândia', 'Population': '12538', 'State': 'AC'},
        {'Area': '186.53', 'Name': 'Boca da Mata', 'Population': '25776', 'State': 'AL'},
        {'Area': '242.62', 'Name': 'Capela', 'Population': '17077', 'State': 'AL'},
    ]


# Issues

def test_preserve_resource_format_from_descriptor_on_infer_issue_188():
    resource = Resource({'path': 'data/data.csvformat', 'format': 'csv'})
    assert resource.infer() == {
        'encoding': 'utf-8',
        'format': 'csv',
        'mediatype': 'text/csv',
        'name': 'data',
        'path': 'data/data.csvformat',
        'profile': 'tabular-data-resource',
        'schema': {'fields': [
            {'format': 'default', 'name': 'city', 'type': 'string'},
            {'format': 'default', 'name': 'population', 'type': 'integer'}],
            'missingValues': ['']}}


# Helpers

@pytest.fixture
def patch_get():
    httpretty.enable()
    yield partial(httpretty.register_uri, httpretty.GET)
    httpretty.disable()
    httpretty.reset()

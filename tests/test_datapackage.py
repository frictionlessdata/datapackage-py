 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest
import httpretty
import tests.test_helpers as test_helpers
import datapackage


class TestDataPackage(object):
    def test_init_uses_base_schema_by_default(self):
        dp = datapackage.DataPackage()
        assert dp.schema.title == 'DataPackage'

    def test_init_accepts_dicts(self):
        metadata = {
            'foo': 'bar',
        }
        dp = datapackage.DataPackage(metadata)
        assert dp.to_dict() == metadata

    def test_init_accepts_file_paths(self):
        path = test_helpers.fixture_path('empty_datapackage.json')
        dp = datapackage.DataPackage(path)
        assert dp.to_dict() == {}

    def test_init_raises_if_file_path_doesnt_exist(self):
        path = 'this-file-doesnt-exist.json'
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(path)

    def test_init_raises_if_path_isnt_a_json(self):
        not_a_json_path = test_helpers.fixture_path('not_a_json')
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(not_a_json_path)

    def test_init_raises_if_path_json_isnt_a_dict(self):
        empty_array_path = test_helpers.fixture_path('empty_array.json')
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(empty_array_path)

    def test_init_raises_if_metadata_isnt_dict_or_string(self):
        metadata = 51
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(metadata)

    def test_schema(self):
        metadata = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(metadata, schema=schema)
        assert dp.schema.to_dict() == schema

    def test_attributes(self):
        metadata = {
            'name': 'test',
            'title': 'a test',
        }
        schema = {
            'properties': {
                'name': {}
            }
        }
        dp = datapackage.DataPackage(metadata, schema)
        assert sorted(dp.attributes) == sorted(['name', 'title'])

    def test_attributes_can_be_set(self):
        metadata = {
            'name': 'foo',
        }
        dp = datapackage.DataPackage(metadata)
        dp.metadata['title'] = 'bar'
        assert dp.to_dict() == {'name': 'foo', 'title': 'bar'}

    def test_attributes_arent_immutable(self):
        metadata = {
            'keywords': [],
        }
        dp = datapackage.DataPackage(metadata)
        dp.metadata['keywords'].append('foo')
        assert dp.to_dict() == {'keywords': ['foo']}

    def test_attributes_return_an_empty_list_if_there_are_none(self):
        metadata = {}
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        assert dp.attributes == []

    def test_validate(self):
        metadata = {
            'name': 'foo',
        }
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(metadata, schema)
        dp.validate()

    def test_validate_works_when_setting_attributes_after_creation(self):
        schema = {
            'properties': {
                'name': {}
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(schema=schema)
        dp.metadata['name'] = 'foo'
        dp.validate()

    def test_validate_raises_validation_error_if_invalid(self):
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(schema=schema)
        with pytest.raises(datapackage.exceptions.ValidationError):
            dp.validate()

    def test_required_attributes(self):
        schema = {
            'required': ['name', 'title'],
        }
        dp = datapackage.DataPackage(schema=schema)
        assert dp.required_attributes == ['name', 'title']

    def test_required_attributes_returns_empty_list_if_nothings_required(self):
        schema = {}
        dp = datapackage.DataPackage(schema=schema)
        assert dp.required_attributes == []


class TestDataPackageResources(object):
    def test_base_path_defaults_to_none(self):
        assert datapackage.DataPackage().base_path is None

    def test_base_path_cant_be_set_directly(self):
        dp = datapackage.DataPackage()
        with pytest.raises(AttributeError):
            dp.base_path = 'foo'

    def test_base_path_can_be_set_by_changing_the_metadata(self):
        metadata = {}
        dp = datapackage.DataPackage(metadata, default_base_path='foo')
        assert dp.base_path == 'foo'
        dp.metadata['base'] = 'metadata/base/path'
        assert dp.base_path == 'metadata/base/path'

    def test_base_path_passed_through_data_is_prefered_over_the_default(self):
        metadata = {
            'base': 'metadata/base/path'
        }
        dp = datapackage.DataPackage(metadata, default_base_path='foo')
        assert dp.base_path == 'metadata/base/path'

    def test_base_path_is_default_when_metadata_is_a_dict(self):
        metadata = {}
        dp = datapackage.DataPackage(metadata, default_base_path='foo')
        assert dp.base_path == 'foo'

    def test_base_path_is_datapackages_base_path_when_it_is_a_file(self):
        path = test_helpers.fixture_path('empty_datapackage.json')
        base_path = os.path.dirname(path)
        dp = datapackage.DataPackage(path)
        assert dp.base_path == base_path

    def test_resources_are_empty_tuple_by_default(self):
        metadata = {}
        dp = datapackage.DataPackage(metadata)
        assert dp.resources == ()

    def test_cant_assign_to_resources(self):
        metadata = {}
        dp = datapackage.DataPackage(metadata)
        with pytest.raises(AttributeError):
            dp.resources = ()

    def test_inline_resources_are_loaded(self):
        metadata = {
            'resources': [
                {'data': 'foo'},
                {'data': 'bar'},
            ],
        }
        dp = datapackage.DataPackage(metadata)
        assert len(dp.resources) == 2
        assert dp.resources[0].data == 'foo'
        assert dp.resources[1].data == 'bar'

    def test_local_resource_with_absolute_path_is_loaded(self):
        path = test_helpers.fixture_path('unicode.txt')
        metadata = {
            'resources': [
                {'path': path},
            ],
        }
        dp = datapackage.DataPackage(metadata)
        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难\n'

    def test_local_resource_with_relative_path_is_loaded(self):
        datapackage_filename = 'datapackage_with_unicode.txt_resource.json'
        path = test_helpers.fixture_path(datapackage_filename)
        dp = datapackage.DataPackage(path)
        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难\n'

    def test_raises_if_local_resource_path_doesnt_exist(self):
        metadata = {
            'resources': [
                {'path': 'inexistent-file.json'},
            ],
        }

        with pytest.raises(datapackage.exceptions.ResourceError):
            datapackage.DataPackage(metadata)

    @httpretty.activate
    def test_remote_resource_is_loaded(self):
        url = 'http://someplace.com/resource.txt'
        body = '万事开头难'
        httpretty.register_uri(httpretty.GET, url, body=body)
        metadata = {
            'resources': [
                {'url': url},
            ],
        }

        # FIXME: Remove explicit schema whenever datapackage_registry caches
        # its schemas
        dp = datapackage.DataPackage(metadata, schema={})
        assert len(dp.resources) == 1
        assert dp.resources[0].data == body

    @httpretty.activate
    def test_raises_if_remote_resource_url_doesnt_exist(self):
        url = 'http://someplace.com/inexistent-file.json'
        httpretty.register_uri(httpretty.GET, url, status=404)
        metadata = {
            'resources': [
                {'url': url},
            ],
        }

        # FIXME: Remove explicit schema whenever datapackage_registry caches
        # its schemas
        with pytest.raises(datapackage.exceptions.ResourceError):
            datapackage.DataPackage(metadata, schema={})

 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    import mock
except ImportError:
    import unittest.mock as mock

import os
import glob
import json
import tempfile
import zipfile
import pytest
import httpretty
import tests.test_helpers as test_helpers
import datapackage_registry
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
        assert dp.metadata == metadata

    def test_init_accepts_file_paths(self):
        path = test_helpers.fixture_path('empty_datapackage.json')
        dp = datapackage.DataPackage(path)
        assert dp.metadata == {}

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

    @httpretty.activate
    def test_init_accepts_urls(self):
        url = 'http://someplace.com/datapackage.json'
        body = '{"foo": "bar"}'
        httpretty.register_uri(httpretty.GET, url, body=body,
                               content_type='application/json')

        dp = datapackage.DataPackage(url)
        assert dp.metadata == {'foo': 'bar'}

    @httpretty.activate
    def test_init_raises_if_url_doesnt_exist(self):
        url = 'http://someplace.com/datapackage.json'
        httpretty.register_uri(httpretty.GET, url, status=404)

        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(url)

    @httpretty.activate
    def test_init_raises_if_url_isnt_a_json(self):
        url = 'http://someplace.com/datapackage.json'
        body = 'Not a JSON'
        httpretty.register_uri(httpretty.GET, url, body=body,
                               content_type='application/json')

        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(url)

    @httpretty.activate
    def test_init_raises_if_url_json_isnt_a_dict(self):
        url = 'http://someplace.com/datapackage.json'
        body = '["foo"]'
        httpretty.register_uri(httpretty.GET, url, body=body,
                               content_type='application/json')

        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(url)

    def test_init_raises_if_metadata_isnt_dict_or_string(self):
        metadata = 51
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(metadata)

    def test_schema(self):
        metadata = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(metadata, schema=schema)
        assert dp.schema.to_dict() == schema

    @mock.patch('datapackage_registry.Registry')
    def test_schema_gets_from_registry_if_available(self, registry_class_mock):
        schema = {'foo': 'bar'}
        registry_mock = mock.MagicMock()
        registry_mock.get.return_value = schema
        registry_class_mock.return_value = registry_mock

        assert datapackage.DataPackage().schema.to_dict() == schema

    @mock.patch('datapackage_registry.Registry')
    def test_schema_raises_schemaerror_if_registry_raised(self,
                                                          registry_class_mock):
        registry_ex = datapackage_registry.exceptions
        DataPackageRegistryException = registry_ex.DataPackageRegistryException
        registry_class_mock.side_effect = DataPackageRegistryException

        with pytest.raises(datapackage.exceptions.SchemaError):
            datapackage.DataPackage()

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

    def test_attributes_return_an_empty_tuple_if_there_are_none(self):
        metadata = {}
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        assert dp.attributes == ()

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
        assert dp.required_attributes == ('name', 'title')

    def test_required_attributes_return_empty_tuple_if_nothings_required(self):
        schema = {}
        dp = datapackage.DataPackage(schema=schema)
        assert dp.required_attributes == ()

    def test_to_dict_value_can_be_altered_without_changing_the_dp(self):
        metadata = {}
        dp = datapackage.DataPackage(metadata)
        dp_dict = dp.to_dict()
        dp_dict['foo'] = 'bar'
        assert dp.metadata == {}

    def test_to_json(self):
        metadata = {
            'foo': 'bar',
        }
        dp = datapackage.DataPackage(metadata)
        assert json.loads(dp.to_json()) == metadata


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

    @httpretty.activate
    def test_base_path_is_set_to_base_url_when_datapackage_is_in_url(self):
        base_url = 'http://someplace.com/data'
        url = '{base_url}/datapackage.json'.format(base_url=base_url)
        body = '{}'
        httpretty.register_uri(httpretty.GET, url, body=body)
        dp = datapackage.DataPackage(url)
        assert dp.base_path == base_url

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

        dp = datapackage.DataPackage(metadata)
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

        with pytest.raises(datapackage.exceptions.ResourceError):
            datapackage.DataPackage(metadata)

    def test_changing_resource_metadata_changes_it_in_the_datapackage(self):
        metadata = {
            'resources': [
                {
                    'data': '万事开头难',
                }
            ]
        }

        dp = datapackage.DataPackage(metadata)
        dp.resources[0].metadata['name'] = 'saying'
        assert dp.to_dict()['resources'][0]['name'] == 'saying'

    def test_can_add_resource(self):
        resource = {
            'data': '万事开头难',
        }
        dp = datapackage.DataPackage()
        resources = dp.metadata.get('resources', [])
        resources.append(resource)
        dp.metadata['resources'] = resources

        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难'

    def test_can_remove_resource(self):
        metadata = {
            'resources': [
                {'data': '万事开头难'},
                {'data': 'All beginnings are hard'}
            ]
        }
        dp = datapackage.DataPackage(metadata)
        del dp.metadata['resources'][1]

        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难'


class TestSavingDataPackages(object):
    @pytest.yield_fixture
    def tmpfile(self):
        with tempfile.NamedTemporaryFile() as f:
            yield f

    def test_saves_as_zip(self, tmpfile):
        dp = datapackage.DataPackage(schema={})
        dp.save(tmpfile)
        assert zipfile.is_zipfile(tmpfile)

    def test_accepts_file_paths(self, tmpfile):
        dp = datapackage.DataPackage(schema={})
        dp.save(tmpfile.name)
        assert zipfile.is_zipfile(tmpfile.name)

    def test_adds_datapackage_descriptor_at_zipfile_root(self, tmpfile):
        metadata = {
            'name': 'proverbs',
            'resources': [
                {'data': '万事开头难'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            dp_json = z.read('datapackage.json').decode('utf-8')
        assert json.loads(dp_json) == json.loads(dp.to_json())

    def test_generates_filenames_for_named_resources(self, tmpfile):
        resource_path = test_helpers.fixture_path('unicode.txt')
        metadata = {
            'name': 'proverbs',
            'resources': [
                {'name': 'proverbs', 'format': 'TXT', 'path': resource_path},
                {'name': 'proverbs_without_format', 'path': resource_path}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            assert 'data/proverbs.txt' in z.namelist()
            assert 'data/proverbs_without_format' in z.namelist()

    def test_generates_unique_filenames_for_unnamed_resources(self, tmpfile):
        metadata = {
            'name': 'proverbs',
            'resources': [
                {'path': test_helpers.fixture_path('unicode.txt')},
                {'path': test_helpers.fixture_path('foo.txt')}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            files = z.namelist()
            assert sorted(set(files)) == sorted(files)

    def test_adds_resources_inside_data_subfolder(self, tmpfile):
        resource_path = test_helpers.fixture_path('unicode.txt')
        metadata = {
            'name': 'proverbs',
            'resources': [
                {'path': resource_path}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            filename = [name for name in z.namelist()
                        if name.startswith('data/')]
            assert len(filename) == 1
            resource_data = z.read(filename[0]).decode('utf-8')
        assert resource_data == '万事开头难\n'

    def test_fixes_resources_paths_to_be_relative_to_package(self, tmpfile):
        resource_path = test_helpers.fixture_path('unicode.txt')
        metadata = {
            'name': 'proverbs',
            'resources': [
                {'name': 'unicode', 'format': 'txt', 'path': resource_path}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            json_string = z.read('datapackage.json').decode('utf-8')
            generated_dp_dict = json.loads(json_string)
        assert generated_dp_dict['resources'][0]['path'] == 'data/unicode.txt'

    def test_works_with_resources_with_relative_paths(self, tmpfile):
        base_path = test_helpers.fixture_path('')
        metadata = {
            'name': 'proverbs',
            'base': base_path,
            'resources': [
                {'path': 'unicode.txt'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(metadata, schema)
        dp.save(tmpfile)

    def test_should_raise_validation_error_if_datapackage_is_invalid(self,
                                                                     tmpfile):
        metadata = {}
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(metadata, schema)
        with pytest.raises(datapackage.exceptions.ValidationError):
            dp.save(tmpfile)

    def test_should_raise_if_path_doesnt_exist(self):
        dp = datapackage.DataPackage({}, {})

        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp.save('/non/existent/file/path')

    @mock.patch('zipfile.ZipFile')
    def test_should_raise_if_zipfile_raised_BadZipfile(self,
                                                       zipfile_mock,
                                                       tmpfile):
        zipfile_mock.side_effect = zipfile.BadZipfile()
        dp = datapackage.DataPackage({}, {})

        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp.save(tmpfile)

    @mock.patch('zipfile.ZipFile')
    def test_should_raise_if_zipfile_raised_LargeZipFile(self,
                                                         zipfile_mock,
                                                         tmpfile):
        zipfile_mock.side_effect = zipfile.LargeZipFile()
        dp = datapackage.DataPackage({}, {})

        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp.save(tmpfile)


class TestImportingDataPackageFromZip(object):
    @pytest.yield_fixture
    def datapackage_zip(self):
        with tempfile.NamedTemporaryFile() as f:
            metadata = {
                'name': 'proverbs',
                'resources': [
                    {'path': test_helpers.fixture_path('unicode.txt')},
                ]
            }
            dp = datapackage.DataPackage(metadata)
            dp.save(f)
            yield f

    def test_it_works_with_local_paths(self, datapackage_zip):
        dp = datapackage.DataPackage(datapackage_zip.name)
        assert dp.metadata['name'] == 'proverbs'
        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难\n'

    def test_it_works_with_file_objects(self, datapackage_zip):
        dp = datapackage.DataPackage(datapackage_zip)
        assert dp.metadata['name'] == 'proverbs'
        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难\n'

    def test_it_works_with_remote_files(self, datapackage_zip):
        httpretty.enable()

        datapackage_zip.seek(0)
        url = 'http://someplace.com/datapackage.zip'
        httpretty.register_uri(httpretty.GET, url, body=datapackage_zip.read(),
                               content_type='application/zip')

        dp = datapackage.DataPackage(url)
        assert dp.metadata['name'] == 'proverbs'
        assert len(dp.resources) == 1
        assert dp.resources[0].data == '万事开头难\n'

        httpretty.disable()

    def test_it_removes_temporary_directories(self, datapackage_zip):
        tempdirs_glob = os.path.join(tempfile.gettempdir(), '*-datapackage')
        original_tempdirs = glob.glob(tempdirs_glob)
        dp = datapackage.DataPackage(datapackage_zip)
        dp.save(datapackage_zip)

        assert glob.glob(tempdirs_glob) == original_tempdirs

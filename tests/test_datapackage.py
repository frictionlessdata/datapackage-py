 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import glob
import json
import mock
import tempfile
import zipfile
import six
import pytest
import httpretty
import tests.test_helpers as test_helpers
import datapackage
from datapackage import helpers


# Tests

class TestDataPackage(object):
    def test_init_uses_base_schema_by_default(self):
        dp = datapackage.DataPackage()
        assert dp.schema.title == 'Data Package'

    def test_init_accepts_dicts(self):
        descriptor = {
            'profile': 'data-package',
        }
        dp = datapackage.DataPackage(descriptor)
        assert dp.descriptor == descriptor

    def test_init_accepts_filelike_object(self):
        descriptor = {
            'profile': 'data-package',
        }
        filelike_descriptor = six.StringIO(json.dumps(descriptor))
        dp = datapackage.DataPackage(filelike_descriptor)
        assert dp.descriptor == descriptor

    def test_init_accepts_file_paths(self):
        path = test_helpers.fixture_path('empty_datapackage.json')
        dp = datapackage.DataPackage(path)
        assert dp.descriptor == {
            'profile': 'data-package',
        }

    def test_init_raises_if_file_path_doesnt_exist(self):
        path = 'this-file-doesnt-exist.json'
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(path)

    def test_init_raises_if_path_isnt_a_json(self):
        not_a_json_path = test_helpers.fixture_path('not_a_json')
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(not_a_json_path)

    def test_init_raises_if_path_is_a_bad_json(self):
        bad_json = test_helpers.fixture_path('bad_json.json')
        with pytest.raises(datapackage.exceptions.DataPackageException) as excinfo:
            datapackage.DataPackage(bad_json)
        message = str(excinfo.value)
        assert 'Unable to parse JSON' in message
        assert 'line 2 column 5 (char 6)' in message

    def test_init_raises_if_path_json_isnt_a_dict(self):
        empty_array_path = test_helpers.fixture_path('empty_array.json')
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(empty_array_path)

    def test_init_raises_if_filelike_object_isnt_a_json(self):
        invalid_json = six.StringIO(
            '{"foo"}'
        )
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(invalid_json)

    @httpretty.activate
    def test_init_accepts_urls(self):
        url = 'http://someplace.com/datapackage.json'
        body = '{"profile": "data-package"}'
        httpretty.register_uri(httpretty.GET, url, body=body,
                               content_type='application/json')

        dp = datapackage.DataPackage(url)
        assert dp.descriptor == {'profile': 'data-package'}

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

    def test_init_raises_if_descriptor_isnt_dict_or_string(self):
        descriptor = 51
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(descriptor)

    def test_schema(self):
        descriptor = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(descriptor, schema=schema)
        assert dp.schema.to_dict() == schema

    @mock.patch('datapackage.registry.Registry')
    def test_schema_gets_from_registry_if_available(self, registry_class_mock):
        schema = {'foo': 'bar'}
        registry_mock = mock.MagicMock()
        registry_mock.get.return_value = schema
        registry_class_mock.return_value = registry_mock

        assert datapackage.DataPackage().schema.to_dict() == schema

    @mock.patch('datapackage.registry.Registry')
    def test_schema_raises_registryerror_if_registry_raised(self,
                                                            registry_mock):
        registry_mock.side_effect = datapackage.exceptions.RegistryError

        with pytest.raises(datapackage.exceptions.RegistryError):
            datapackage.DataPackage()

    def test_attributes(self):
        descriptor = {
            'name': 'test',
            'title': 'a test',
            'profile': 'data-package',
        }
        schema = {
            'properties': {
                'name': {}
            }
        }
        dp = datapackage.DataPackage(descriptor, schema)
        assert sorted(dp.attributes) == sorted(['name', 'title', 'profile'])

    def test_attributes_can_be_set(self):
        descriptor = {
            'profile': 'data-package',
        }
        dp = datapackage.DataPackage(descriptor)
        dp.descriptor['title'] = 'bar'
        assert dp.to_dict() == {'profile': 'data-package', 'title': 'bar'}

    def test_attributes_arent_immutable(self):
        descriptor = {
            'profile': 'data-package',
            'keywords': [],
        }
        dp = datapackage.DataPackage(descriptor)
        dp.descriptor['keywords'].append('foo')
        assert dp.to_dict() == {'profile': 'data-package', 'keywords': ['foo']}

    def test_attributes_return_defaults_id_descriptor_is_empty(self):
        descriptor = {}
        schema = {}
        dp = datapackage.DataPackage(descriptor, schema)
        assert dp.attributes == ('profile',)

    def test_validate(self):
        descriptor = {
            'name': 'foo',
        }
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(descriptor, schema)
        dp.validate()

    def test_validate_works_when_setting_attributes_after_creation(self):
        schema = {
            'properties': {
                'name': {}
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(schema=schema)
        dp.descriptor['name'] = 'foo'
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

    @mock.patch('datapackage.schema.Schema')
    def test_iter_errors_returns_schemas_iter_errors(self, schema_mock):
        iter_errors_mock = mock.Mock()
        iter_errors_mock.return_value = 'the iter errors'
        schema_mock.return_value.iter_errors = iter_errors_mock

        descriptor = {}
        dp = datapackage.DataPackage(descriptor)

        assert dp.iter_errors() == 'the iter errors'
        iter_errors_mock.assert_called_with(dp.to_dict())

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
        descriptor = {
            'profile': 'data-package',
        }
        dp = datapackage.DataPackage(descriptor)
        dp_dict = dp.to_dict()
        dp_dict['foo'] = 'bar'
        assert dp.descriptor == {
            'profile': 'data-package',
        }

    def test_to_json(self):
        descriptor = {
            'foo': 'bar',
        }
        dp = datapackage.DataPackage(descriptor)
        assert json.loads(dp.to_json()) == descriptor

    def test_descriptor_dereferencing_uri(self):
        dp = datapackage.DataPackage('tests/fixtures/datapackage_with_dereferencing.json')
        assert dp.descriptor['resources'] == list(map(helpers.expand_resource_descriptor, [
            {'name': 'name1', 'data': 'data', 'schema': {'fields': [{'name': 'name'}]}},
            {'name': 'name2', 'data': 'data', 'dialect': {'delimiter': ','}},
        ]))

    def test_descriptor_dereferencing_uri_pointer(self):
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': '#/schemas/main'},
                {'name': 'name2', 'data': 'data', 'dialect': '#/dialects/0'},
             ],
            'schemas': {'main': {'fields': [{'name': 'name'}]}},
            'dialects': [{'delimiter': ','}],
        }
        dp = datapackage.DataPackage(descriptor)
        assert dp.descriptor['resources'] == list(map(helpers.expand_resource_descriptor, [
            {'name': 'name1', 'data': 'data', 'schema': {'fields': [{'name': 'name'}]}},
            {'name': 'name2', 'data': 'data', 'dialect': {'delimiter': ','}},
        ]))

    def test_descriptor_dereferencing_uri_pointer_bad(self):
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': '#/schemas/main'},
             ],
        }
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(descriptor)

    @httpretty.activate
    def test_descriptor_dereferencing_uri_remote(self):
        # Mocks
        httpretty.register_uri(httpretty.GET,
            'http://example.com/schema', body='{"fields": [{"name": "name"}]}')
        httpretty.register_uri(httpretty.GET,
            'https://example.com/dialect', body='{"delimiter": ","}')
        # Tests
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': 'http://example.com/schema'},
                {'name': 'name2', 'data': 'data', 'dialect': 'https://example.com/dialect'},
             ],
        }
        dp = datapackage.DataPackage(descriptor)
        assert dp.descriptor['resources'] == list(map(helpers.expand_resource_descriptor, [
            {'name': 'name1', 'data': 'data', 'schema': {'fields': [{'name': 'name'}]}},
            {'name': 'name2', 'data': 'data', 'dialect': {'delimiter': ','}},
        ]))

    def test_descriptor_dereferencing_uri_remote_bad(self):
        # Mocks
        httpretty.register_uri(httpretty.GET, 'http://example.com/schema', status=404)
        # Tests
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': 'http://example.com/schema'},
             ],
        }
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(descriptor)

    def test_descriptor_dereferencing_uri_local(self):
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': 'table_schema.json'},
                {'name': 'name2', 'data': 'data', 'dialect': 'csv_dialect.json'},
             ],
        }
        dp = datapackage.DataPackage(descriptor, default_base_path='tests/fixtures')
        assert dp.descriptor['resources'] == list(map(helpers.expand_resource_descriptor, [
            {'name': 'name1', 'data': 'data', 'schema': {'fields': [{'name': 'name'}]}},
            {'name': 'name2', 'data': 'data', 'dialect': {'delimiter': ','}},
        ]))

    def test_descriptor_dereferencing_uri_local_bad(self):
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': 'bad_path.json'},
             ],
        }
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(descriptor, default_base_path='tests/fixtures')

    def test_descriptor_dereferencing_uri_local_bad_not_safe(self):
        descriptor = {
            'resources': [
                {'name': 'name1', 'data': 'data', 'schema': '../fixtures/table_schema.json'},
             ],
        }
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(descriptor, default_base_path='tests/fixtures')

    def test_descriptor_apply_defaults(self):
        descriptor = {}
        dp = datapackage.DataPackage(descriptor)
        assert descriptor == {
            'profile': 'data-package',
        }

    def test_descriptor_apply_defaults_resource(self):
        descriptor = {
            'resources': [{'name': 'name', 'data': 'data'}],
        }
        dp = datapackage.DataPackage(descriptor)
        assert descriptor == {
            'profile': 'data-package',
            'resources': [
                {'name': 'name', 'data': 'data', 'profile': 'data-resource', 'encoding': 'utf-8'},
            ]
        }

    def test_descriptor_apply_defaults_resource_tabular_schema(self):
        descriptor = {
            'resources': [{
                'name': 'name',
                'data': 'data',
                'profile': 'tabular-data-resource',
                'schema': {
                    'fields': [{'name': 'name'}],
                }
            }],
        }
        dp = datapackage.DataPackage(descriptor)
        assert descriptor == {
            'profile': 'data-package',
            'resources': [{
                'name': 'name',
                'data': 'data',
                'profile': 'tabular-data-resource',
                'encoding': 'utf-8',
                'schema': {
                    'fields': [{'name': 'name', 'type': 'string', 'format': 'default'}],
                    'missingValues': [''],
                }
            }],
        }

    def test_descriptor_apply_defaults_resource_tabular_dialect(self):
        descriptor = {
            'resources': [{
                'name': 'name',
                'data': 'data',
                'profile': 'tabular-data-resource',
                'dialect': {
                    'delimiter': 'custom',
                }
            }],
        }
        dp = datapackage.DataPackage(descriptor)
        assert descriptor == {
            'profile': 'data-package',
            'resources': [{
                'name': 'name',
                'data': 'data',
                'profile': 'tabular-data-resource',
                'encoding': 'utf-8',
                'dialect': {
                    'delimiter': 'custom',
                    'doubleQuote': True,
                    'lineTerminator': '\r\n',
                    'quoteChar': '"',
                    'escapeChar': '\\',
                    'skipInitialSpace': True,
                    'header': True,
                    'caseSensitiveHeader': False,
                }
            }],
        }


class TestDataPackageResources(object):
    def test_base_path_defaults_to_none(self):
        assert datapackage.DataPackage().base_path is None

    def test_base_path_cant_be_set_directly(self):
        dp = datapackage.DataPackage()
        with pytest.raises(AttributeError):
            dp.base_path = 'foo'

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
        descriptor = {}
        dp = datapackage.DataPackage(descriptor)
        assert dp.resources == ()

    def test_cant_assign_to_resources(self):
        descriptor = {}
        dp = datapackage.DataPackage(descriptor)
        with pytest.raises(AttributeError):
            dp.resources = ()

    def test_inline_resources_are_loaded(self):
        descriptor = {
            'resources': [
                {'data': 'foo'},
                {'data': 'bar'},
            ],
        }
        dp = datapackage.DataPackage(descriptor)
        assert len(dp.resources) == 2
        assert dp.resources[0].source == 'foo'
        assert dp.resources[1].source == 'bar'

    def test_local_resource_with_relative_path_is_loaded(self):
        datapackage_filename = 'datapackage_with_foo.txt_resource.json'
        path = test_helpers.fixture_path(datapackage_filename)
        dp = datapackage.DataPackage(path)
        assert len(dp.resources) == 1
        assert dp.resources[0].source.endswith('foo.txt')

    @httpretty.activate
    def test_remote_resource_is_loaded(self):
        url = 'http://someplace.com/resource.txt'
        httpretty.register_uri(httpretty.GET, url, body='foo')
        descriptor = {
            'resources': [
                {'url': url},
            ],
        }

        dp = datapackage.DataPackage(descriptor)
        assert len(dp.resources) == 1
        assert dp.resources[0].source == 'http://someplace.com/resource.txt'

    def test_changing_resource_descriptor_changes_it_in_the_datapackage(self):
        descriptor = {
            'resources': [
                {
                    'data': '万事开头难',
                }
            ]
        }

        dp = datapackage.DataPackage(descriptor)
        dp.resources[0].descriptor['name'] = 'saying'
        assert dp.to_dict()['resources'][0]['name'] == 'saying'

    def test_can_add_resource(self):
        resource = {
            'data': '万事开头难',
        }
        dp = datapackage.DataPackage()
        resources = dp.descriptor.get('resources', [])
        resources.append(resource)
        dp.descriptor['resources'] = resources

        assert len(dp.resources) == 1
        assert dp.resources[0].source == '万事开头难'

    def test_can_remove_resource(self):
        descriptor = {
            'resources': [
                {'data': '万事开头难'},
                {'data': 'All beginnings are hard'}
            ]
        }
        dp = datapackage.DataPackage(descriptor)
        del dp.descriptor['resources'][1]

        assert len(dp.resources) == 1
        assert dp.resources[0].source == '万事开头难'


class TestSavingDataPackages(object):
    def test_saves_as_zip(self, tmpfile):
        dp = datapackage.DataPackage(schema={})
        dp.save(tmpfile)
        assert zipfile.is_zipfile(tmpfile)

    def test_accepts_file_paths(self, tmpfile):
        dp = datapackage.DataPackage(schema={})
        dp.save(tmpfile.name)
        assert zipfile.is_zipfile(tmpfile.name)

    def test_adds_datapackage_descriptor_at_zipfile_root(self, tmpfile):
        descriptor = {
            'name': 'proverbs',
            'resources': [
                {'data': '万事开头难'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(descriptor, schema)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            dp_json = z.read('datapackage.json').decode('utf-8')
        assert json.loads(dp_json) == json.loads(dp.to_json())

    def test_generates_filenames_for_named_resources(self, tmpfile):
        descriptor = {
            'name': 'proverbs',
            'resources': [
                {'name': 'proverbs', 'format': 'TXT', 'path': 'unicode.txt'},
                {'name': 'proverbs_without_format', 'path': 'unicode.txt'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(
            descriptor, schema, default_base_path='tests/fixtures')
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            assert 'data/proverbs.txt' in z.namelist()
            assert 'data/proverbs_without_format' in z.namelist()

    def test_generates_unique_filenames_for_unnamed_resources(self, tmpfile):
        descriptor = {
            'name': 'proverbs',
            'resources': [
                {'path': 'unicode.txt'},
                {'path': 'foo.txt'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(
            descriptor, schema, default_base_path='tests/fixtures')
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            files = z.namelist()
            assert sorted(set(files)) == sorted(files)

    def test_adds_resources_inside_data_subfolder(self, tmpfile):
        descriptor = {
            'name': 'proverbs',
            'resources': [
                {'path': 'unicode.txt'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(
            descriptor, schema, default_base_path='tests/fixtures')
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            filename = [name for name in z.namelist()
                        if name.startswith('data/')]
            assert len(filename) == 1
            resource_data = z.read(filename[0]).decode('utf-8')
        assert resource_data == '万事开头难\n'

    def test_fixes_resources_paths_to_be_relative_to_package(self, tmpfile):
        descriptor = {
            'name': 'proverbs',
            'resources': [
                {'name': 'unicode', 'format': 'txt', 'path': 'unicode.txt'}
            ]
        }
        schema = {}
        dp = datapackage.DataPackage(
            descriptor, schema, default_base_path='tests/fixtures')
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            json_string = z.read('datapackage.json').decode('utf-8')
            generated_dp_dict = json.loads(json_string)
        assert generated_dp_dict['resources'][0]['path'] == 'data/unicode.txt'

    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_works_with_resources_with_relative_paths(self, tmpfile):
        path = test_helpers.fixture_path(
            'datapackage_with_foo.txt_resource.json'
        )
        dp = datapackage.DataPackage(path)
        dp.save(tmpfile)
        with zipfile.ZipFile(tmpfile, 'r') as z:
            assert len(z.filelist) == 2

    def test_should_raise_validation_error_if_datapackage_is_invalid(self,
                                                                     tmpfile):
        descriptor = {}
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(descriptor, schema)
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
    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_it_works_with_local_paths(self, datapackage_zip):
        dp = datapackage.DataPackage(datapackage_zip.name)
        assert dp.descriptor['name'] == 'proverbs'
        assert len(dp.resources) == 1
        assert dp.resources[0].data == b'foo\n'

    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_it_works_with_file_objects(self, datapackage_zip):
        dp = datapackage.DataPackage(datapackage_zip)
        assert dp.descriptor['name'] == 'proverbs'
        assert len(dp.resources) == 1
        assert dp.resources[0].data == b'foo\n'

    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_it_works_with_remote_files(self, datapackage_zip):
        httpretty.enable()

        datapackage_zip.seek(0)
        url = 'http://someplace.com/datapackage.zip'
        httpretty.register_uri(httpretty.GET, url, body=datapackage_zip.read(),
                               content_type='application/zip')

        dp = datapackage.DataPackage(url)
        assert dp.descriptor['name'] == 'proverbs'
        assert len(dp.resources) == 1
        assert dp.resources[0].data == b'foo\n'

        httpretty.disable()

    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_it_removes_temporary_directories(self, datapackage_zip):
        tempdirs_glob = os.path.join(tempfile.gettempdir(), '*-datapackage')
        original_tempdirs = glob.glob(tempdirs_glob)
        dp = datapackage.DataPackage(datapackage_zip)
        dp.save(datapackage_zip)
        del dp

        assert glob.glob(tempdirs_glob) == original_tempdirs

    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_local_data_path(self, datapackage_zip):
        dp = datapackage.DataPackage(datapackage_zip)

        assert dp.resources[0].local_data_path is not None

        with open(test_helpers.fixture_path('foo.txt')) as data_file:
            with open(dp.resources[0].local_data_path) as local_data_file:
                assert local_data_file.read() == data_file.read()

    def test_it_can_load_from_zip_files_inner_folders(self, tmpfile):
        descriptor = {
            'profile': 'data-package',
        }
        with zipfile.ZipFile(tmpfile.name, 'w') as z:
            z.writestr('foo/datapackage.json', json.dumps(descriptor))
        dp = datapackage.DataPackage(tmpfile.name, {})
        assert dp.descriptor == descriptor

    def test_it_breaks_if_theres_no_datapackage_json(self, tmpfile):
        with zipfile.ZipFile(tmpfile.name, 'w') as z:
            z.writestr('data.txt', 'foobar')
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(tmpfile.name, {})

    def test_it_breaks_if_theres_more_than_one_datapackage_json(self, tmpfile):
        descriptor_foo = {
            'name': 'foo',
        }
        descriptor_bar = {
            'name': 'bar',
        }
        with zipfile.ZipFile(tmpfile.name, 'w') as z:
            z.writestr('foo/datapackage.json', json.dumps(descriptor_foo))
            z.writestr('bar/datapackage.json', json.dumps(descriptor_bar))
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(tmpfile.name, {})


class TestSafeDataPackage(object):
    def test_without_resources_is_safe(self):
        descriptor = {}
        dp = datapackage.DataPackage(descriptor, {})
        assert dp.safe()

    def test_with_local_resources_with_inexistent_path_isnt_safe(self):
        descriptor = {
            'resources': [
                {'path': '/foo/bar'},
            ]
        }
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(descriptor, {})

    def test_with_local_resources_with_existent_path_isnt_safe(self):
        descriptor = {
            'resources': [
                {'path': test_helpers.fixture_path('foo.txt')},
            ]
        }
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(descriptor, {})

    def test_descriptor_dict_without_local_resources_is_safe(self):
        descriptor = {
            'resources': [
                {'data': 42},
                {'url': 'http://someplace.com/data.csv'},
            ]
        }
        dp = datapackage.DataPackage(descriptor, {})
        assert dp.safe()

    def test_local_with_relative_resources_paths_is_safe(self):
        fixture_name = 'datapackage_with_foo.txt_resource.json'
        path = test_helpers.fixture_path(fixture_name)
        dp = datapackage.DataPackage(path, {})
        assert dp.safe()

    def test_local_with_resources_outside_base_path_isnt_safe(self, tmpfile):
        descriptor = {
            'resources': [
                {'path': __file__},
            ]
        }
        tmpfile.write(json.dumps(descriptor).encode('utf-8'))
        tmpfile.flush()
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(tmpfile.name, {})

    @pytest.mark.skip(reason='Wait for specs-v1.rc2 resource.data/path')
    def test_zip_with_relative_resources_paths_is_safe(self, datapackage_zip):
        dp = datapackage.DataPackage(datapackage_zip.name, {})
        assert dp.safe()

    def test_zip_with_resources_outside_base_path_isnt_safe(self, tmpfile):
        descriptor = {
            'resources': [
                {'path': __file__},
            ]
        }
        with zipfile.ZipFile(tmpfile.name, 'w') as z:
            z.writestr('datapackage.json', json.dumps(descriptor))
        with pytest.raises(datapackage.exceptions.DataPackageException):
            dp = datapackage.DataPackage(tmpfile.name, {})


# Fixtures

@pytest.fixture
def datapackage_zip(tmpfile):
    descriptor = {
        'name': 'proverbs',
        'resources': [
            {'name': 'name', 'path': 'foo.txt'},
        ]
    }
    dp = datapackage.DataPackage(descriptor, default_base_path='tests/fixtures')
    dp.save(tmpfile)
    return tmpfile

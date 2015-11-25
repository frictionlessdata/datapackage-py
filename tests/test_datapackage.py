import pytest
import tests.test_helpers as test_helpers
import datapackage


class TestDataPackage(object):
    def test_init_uses_base_schema_by_default(self):
        dp = datapackage.DataPackage()
        assert dp.schema.title == 'DataPackage'

    def test_init_accepts_dicts(self):
        data = {
            'foo': 'bar',
        }
        dp = datapackage.DataPackage(data)
        assert dp.to_dict() == data

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

    def test_init_raises_if_data_isnt_dict_or_string(self):
        data = 51
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(data)

    def test_schema(self):
        data = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(data, schema=schema)
        assert dp.schema.to_dict() == schema

    def test_attributes(self):
        data = {
            'name': 'test',
            'title': 'a test',
        }
        schema = {
            'properties': {
                'name': {}
            }
        }
        dp = datapackage.DataPackage(data, schema)
        assert sorted(dp.attributes) == sorted(['name', 'title'])

    def test_attributes_can_be_set(self):
        data = {
            'name': 'foo',
        }
        dp = datapackage.DataPackage(data)
        dp.data['title'] = 'bar'
        assert dp.to_dict() == {'name': 'foo', 'title': 'bar'}

    def test_attributes_arent_immutable(self):
        data = {
            'keywords': [],
        }
        dp = datapackage.DataPackage(data)
        dp.data['keywords'].append('foo')
        assert dp.to_dict() == {'keywords': ['foo']}

    def test_attributes_return_an_empty_list_if_there_are_none(self):
        data = {}
        schema = {}
        dp = datapackage.DataPackage(data, schema)
        assert dp.attributes == []

    def test_validate(self):
        data = {
            'name': 'foo',
        }
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(data, schema)
        dp.validate()

    def test_validate_works_when_setting_attributes_after_creation(self):
        schema = {
            'properties': {
                'name': {}
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(schema=schema)
        dp.data['name'] = 'foo'
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
    def test_resources_are_empty_tuple_by_default(self):
        data = {}
        dp = datapackage.DataPackage(data)
        assert dp.resources == ()

    def test_cant_assign_to_resources(self):
        data = {}
        dp = datapackage.DataPackage(data)
        with pytest.raises(AttributeError):
            dp.resources = ()

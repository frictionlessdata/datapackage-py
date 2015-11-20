import pytest
import tests.test_helpers as test_helpers
import datapackage


class TestDataPackage(object):
    def test_init_uses_base_schema_by_default(self):
        dp = datapackage.DataPackage()
        assert dp.schema.title == 'DataPackage'

    def test_init_accepts_dicts(self):
        descriptor = {
            'foo': 'bar',
        }
        dp = datapackage.DataPackage(descriptor)
        assert dp.to_dict() == descriptor

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
        with pytest.raises(ValueError):
            datapackage.DataPackage(not_a_json_path)

    def test_init_raises_if_descriptor_isnt_dict_or_string(self):
        descriptor = 51
        with pytest.raises(datapackage.exceptions.DataPackageException):
            datapackage.DataPackage(descriptor)

    def test_schema(self):
        descriptor = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(descriptor, schema=schema)
        assert dp.schema.to_dict() == schema

    def test_attributes(self):
        descriptor = {
            'name': 'test',
            'title': 'a test',
        }
        schema = {
            'properties': {
                'name': {}
            }
        }
        dp = datapackage.DataPackage(descriptor, schema)
        assert sorted(dp.attributes) == sorted(['name', 'title'])

    def test_attributes_can_be_set(self):
        descriptor = {
            'name': 'foo',
        }
        dp = datapackage.DataPackage(descriptor)
        dp.title = 'bar'
        assert dp.to_dict() == {'name': 'foo', 'title': 'bar'}

    def test_attributes_arent_immutable(self):
        descriptor = {
            'keywords': [],
        }
        dp = datapackage.DataPackage(descriptor)
        dp.keywords.append('foo')
        assert dp.to_dict() == {'keywords': ['foo']}

    def test_attributes_return_an_empty_list_if_there_are_none(self):
        descriptor = {}
        schema = {}
        dp = datapackage.DataPackage(descriptor, schema)
        assert dp.attributes == []

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
        dp.name = 'foo'
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

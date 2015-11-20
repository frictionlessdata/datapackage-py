import pytest
import tests.test_helpers as test_helpers
import datapackage


class TestSchema(object):
    def test_init_loads_schema_from_dict(self):
        schema_dict = {
            'foo': 'bar'
        }
        schema = datapackage.schema.Schema(schema_dict)

        assert schema.to_dict().keys() == schema_dict.keys()
        assert schema.to_dict()['foo'] == schema_dict['foo']

    def test_init_changing_the_original_schema_dict_doesnt_change_schema(self):
        schema_dict = {
            'foo': 'bar'
        }
        schema = datapackage.schema.Schema(schema_dict)
        schema_dict['bar'] = 'baz'

        assert 'bar' not in schema.to_dict()

    def test_init_loads_schema_from_path(self):
        schema_path = test_helpers.fixture_path('empty_schema.json')
        assert datapackage.schema.Schema(schema_path).to_dict() == {}

    def test_init_raises_if_path_doesnt_exist(self):
        with pytest.raises(datapackage.exceptions.SchemaError):
            datapackage.schema.Schema('inexistent_schema.json')

    def test_init_raises_if_path_isnt_a_json(self):
        not_a_json_path = test_helpers.fixture_path('not_a_json')
        with pytest.raises(ValueError):
            datapackage.schema.Schema(not_a_json_path)

    def test_init_raises_if_schema_isnt_string_nor_dict(self):
        invalid_schema = []
        with pytest.raises(datapackage.exceptions.SchemaError):
            datapackage.schema.Schema(invalid_schema)

    def test_init_raises_if_schema_is_invalid(self):
        invalid_schema = {
            'required': 51,
        }
        with pytest.raises(datapackage.exceptions.SchemaError):
            datapackage.schema.Schema(invalid_schema)

    def test_to_dict_converts_schema_to_dict(self):
        original_schema_dict = {
            'foo': 'bar',
        }
        schema = datapackage.schema.Schema(original_schema_dict)
        assert schema.to_dict() == original_schema_dict

    def test_to_dict_modifying_the_dict_doesnt_modify_the_schema(self):
        original_schema_dict = {
            'foo': 'bar',
        }
        schema = datapackage.schema.Schema(original_schema_dict)
        schema_dict = schema.to_dict()
        schema_dict['bar'] = 'baz'
        assert 'bar' not in schema.to_dict()

    def test_validate(self):
        schema_dict = {
            'properties': {
                'name': {
                    'type': 'string',
                }
            },
            'required': ['name'],
        }
        data = {
            'name': 'Sample Package',
        }
        schema = datapackage.schema.Schema(schema_dict)
        schema.validate(data)

    def test_validate_should_raise_when_invalid(self):
        schema_dict = {
            'properties': {
                'name': {
                    'type': 'string',
                }
            },
            'required': ['name'],
        }
        data = {}
        schema = datapackage.schema.Schema(schema_dict)
        with pytest.raises(datapackage.exceptions.ValidationError):
            schema.validate(data)

    def test_it_creates_properties_for_every_toplevel_attribute(self):
        schema_dict = {
            'foo': 'bar',
            'baz': [],
        }
        schema = datapackage.schema.Schema(schema_dict)
        assert schema.foo == 'bar'
        assert schema.baz == []

    def test_doesnt_allow_changing_properties(self):
        schema_dict = {
            'foo': 'bar',
        }
        schema = datapackage.schema.Schema(schema_dict)
        with pytest.raises(AttributeError):
            schema.foo = 'baz'

    def test_changing_properties_attributes_doesnt_change_the_originals(self):
        schema_dict = {
            'foo': {
                'bar': [],
            }
        }
        schema = datapackage.schema.Schema(schema_dict)
        schema.foo['bar'].append('baz')
        assert schema.foo == {'bar': []}

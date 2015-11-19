import six
import pytest
import datapackage.schema
import tests.test_helpers as test_helpers


class TestSchema(object):
    def test_init_loads_schema_from_dict(self):
        schema_dict = {
            'some-attribute': 'some-value'
        }
        schema = datapackage.schema.Schema(schema_dict)

        assert schema.schema.keys() == schema_dict.keys()
        assert schema.schema['some-attribute'] == schema_dict['some-attribute']

    def test_init_loads_schema_from_path(self):
        schema_path = test_helpers.fixture_path('empty_schema.json')
        assert datapackage.schema.Schema(schema_path).schema == {}

    def test_init_raises_if_path_doesnt_exist(self):
        # FIXME: It would be better to catch these errors on Schema() and raise
        # a single Error type. This would make it easier both for testing and
        # for the package's users.
        if six.PY2:
            expected_exception = IOError
        else:
            expected_exception = FileNotFoundError

        with pytest.raises(expected_exception):
            datapackage.schema.Schema('inexistent_schema.json')

    def test_init_raises_if_path_isnt_a_json(self):
        not_a_json_path = test_helpers.fixture_path('not_a_json')
        with pytest.raises(ValueError):
            datapackage.schema.Schema(not_a_json_path)

    def test_init_raises_if_schema_is_invalid(self):
        invalid_schema = []
        with pytest.raises(datapackage.schema.SchemaError):
            datapackage.schema.Schema(invalid_schema)

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
        with pytest.raises(datapackage.schema.ValidationError):
            schema.validate(data)

import json
import pytest
import httpretty
import tests.test_helpers as test_helpers

import datapackage.exceptions
from datapackage.profile import Profile


class TestProfile(object):
    def test_init_loads_schema_from_dict(self):
        schema_dict = {
            'foo': 'bar'
        }
        schema = Profile(schema_dict)

        assert schema.to_dict().keys() == schema_dict.keys()
        assert schema.to_dict()['foo'] == schema_dict['foo']

    def test_init_changing_the_original_schema_dict_doesnt_change_schema(self):
        schema_dict = {
            'foo': 'bar'
        }
        schema = Profile(schema_dict)
        schema_dict['bar'] = 'baz'

        assert 'bar' not in schema.to_dict()

    def test_init_loads_schema_from_path(self):
        schema_path = test_helpers.fixture_path('empty_schema.json')
        assert Profile(schema_path).to_dict() == {}

    def test_init_raises_if_path_doesnt_exist(self):
        with pytest.raises(datapackage.exceptions.SchemaError):
            Profile('inexistent_schema.json')

    def test_init_raises_if_path_isnt_a_json(self):
        not_a_json_path = test_helpers.fixture_path('not_a_json')
        with pytest.raises(datapackage.exceptions.SchemaError):
            Profile(not_a_json_path)

    @httpretty.activate
    def test_init_loads_schema_from_url(self):
        schema = {
            'foo': 'bar',
        }
        url = 'http://someplace.com/schema.json'
        body = json.dumps(schema)
        httpretty.register_uri(httpretty.GET, url,
                               body=body, content_type='application/json')

        assert Profile(url).to_dict() == schema

    @httpretty.activate
    def test_init_raises_if_url_isnt_a_json(self):
        url = 'https://someplace.com/data-package.csv'
        body = 'not a json'
        httpretty.register_uri(httpretty.GET, url, body=body)

        with pytest.raises(datapackage.exceptions.SchemaError):
            Profile(url).to_dict()

    @httpretty.activate
    def test_init_raises_if_url_doesnt_exist(self):
        url = 'https://inexistent-url.com/data-package.json'
        httpretty.register_uri(httpretty.GET, url, status=404)

        with pytest.raises(datapackage.exceptions.SchemaError):
            Profile(url).to_dict()

    def test_init_raises_if_schema_isnt_string_nor_dict(self):
        invalid_schema = []
        with pytest.raises(datapackage.exceptions.SchemaError):
            Profile(invalid_schema)

    def test_init_raises_if_schema_is_invalid(self):
        invalid_schema = {
            'required': 51,
        }
        with pytest.raises(datapackage.exceptions.SchemaError):
            Profile(invalid_schema)

    def test_to_dict_converts_schema_to_dict(self):
        original_schema_dict = {
            'foo': 'bar',
        }
        schema = Profile(original_schema_dict)
        assert schema.to_dict() == original_schema_dict

    def test_to_dict_modifying_the_dict_doesnt_modify_the_schema(self):
        original_schema_dict = {
            'foo': 'bar',
        }
        schema = Profile(original_schema_dict)
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
        schema = Profile(schema_dict)
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
        schema = Profile(schema_dict)
        with pytest.raises(datapackage.exceptions.ValidationError):
            schema.validate(data)

    def test_it_creates_properties_for_every_toplevel_attribute(self):
        schema_dict = {
            'foo': 'bar',
            'baz': [],
        }
        schema = Profile(schema_dict)
        assert schema.foo == 'bar'
        assert schema.baz == []

    def test_doesnt_allow_changing_schema_properties(self):
        schema_dict = {
            'foo': 'bar',
        }
        schema = Profile(schema_dict)
        with pytest.raises(AttributeError):
            schema.foo = 'baz'

    def test_allow_changing_properties_not_in_schema(self):
        schema_dict = {}
        schema = Profile(schema_dict)
        schema.foo = 'bar'
        assert schema.foo == 'bar'

    def test_raises_if_trying_to_access_inexistent_attribute(self):
        schema_dict = {}
        schema = Profile(schema_dict)
        with pytest.raises(AttributeError):
            schema.this_doesnt_exist

    def test_changing_properties_doesnt_change_the_originals(self):
        schema_dict = {
            'foo': {
                'bar': [],
            }
        }
        schema = Profile(schema_dict)
        schema.foo['bar'].append('baz')
        assert schema.foo == {'bar': []}

    def test_properties_are_visible_with_dir(self):
        schema_dict = {
            'foo': {}
        }
        schema = Profile(schema_dict)
        assert 'foo' in dir(schema)

    def test_schema_properties_doesnt_linger_in_class(self):
        foo_schema_dict = {
            'foo': {}
        }
        bar_schema_dict = {
            'bar': {}
        }
        foo_schema = Profile(foo_schema_dict)
        bar_schema = Profile(bar_schema_dict)

        assert 'bar' not in dir(foo_schema)
        assert 'foo' not in dir(bar_schema)

    def test_iter_validation_returns_iter_with_each_validationerror(self):
        schema_dict = {
            'type': 'array',
            'items': {'enum': [1, 2, 3]},
            'maxItems': 2,
        }
        data_dict = [2, 3, 4]
        expected_errors_validators = ('maxItems', 'enum')

        schema = Profile(schema_dict)
        errors = [error for error in schema.iter_errors(data_dict)]

        assert len(errors) == 2
        for error in errors:
            assert error.validator in expected_errors_validators
            assert isinstance(error, datapackage.exceptions.ValidationError)

    def test_iter_validation_returns_no_errors_if_data_is_valid(self):
        schema_dict = {}
        data_dict = ''

        schema = Profile(schema_dict)
        errors = [error for error in schema.iter_errors(data_dict)]

        assert len(errors) == 0

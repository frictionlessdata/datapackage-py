from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import pytest
try:
    import mock
except ImportError:
    import unittest.mock as mock

import httpretty

import datapackage_registry
import datapackage_validate
import datapackage_validate.exceptions as exceptions


REGISTRY_BACKEND_URL = \
    "https://rawgit.com/dataprotocols/registry/master/registry.csv"

REGISTRY_BODY = """id,title,schema,specification
base,Data Package,https://example.com/base_schema.json,http://example.com
tabular,Tabular Data Package,https://example.com/tabular_schema.json,http://example.com"""


def _get_local_base_datapackage_schema():
    schema_path = os.path.join(os.path.dirname(__file__), 'schemas')
    schema_file = os.path.join(schema_path, 'data-package.json')

    with io.open(schema_file) as stream:
        return stream.read()


class TestValidDatapackageJson(object):

    '''The datapackage json itself is well formed'''

    @httpretty.activate
    def test_valid_json_string(self):
        '''validate() returns True with no error messages.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        datapackage_json_str = """{
  "name": "basic-data-package",
  "title": "Basic Data Package"
}"""
        datapackage_validate.validate(datapackage_json_str)

    @httpretty.activate
    def test_invalid_json_string(self):
        '''Datapackage JSON string is not well formed. Retrn False with
        expected error message.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        # missing closing bracket
        invalid_datapackage_json_str = """{
  "name": "basic-data-package",
  "title": "Basic Data Package"
"""
        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(invalid_datapackage_json_str)

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0],
                          exceptions.DataPackageValidateException)

    @httpretty.activate
    def test_invalid_json_not_string(self):
        '''Datapackage isn't a JSON string. Return False with expected error
        message.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        # not a string
        invalid_datapackage_json_str = 123
        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(invalid_datapackage_json_str)

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0],
                          exceptions.DataPackageValidateException)

    @httpretty.activate
    def test_valid_json_obj(self):
        '''Datapackage as valid Python dict.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        datapackage_json_str = """{
  "name": "basic-data-package",
  "title": "Basic Data Package"
}"""
        datapackage_obj = json.loads(datapackage_json_str)
        datapackage_validate.validate(datapackage_obj)

    @httpretty.activate
    def test_invalid_json_obj(self):
        '''Datapackage as invalid Python dict.

        Datapackage is well-formed JSON, but doesn't validate against schema.
        '''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        datapackage_json_str = """{
  "asdf": "1234",
  "qwer": "abcd"
}"""
        datapackage_obj = json.loads(datapackage_json_str)
        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(datapackage_obj)

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0], exceptions.ValidationError)
        assert "'name' is a required property" in str(excinfo.value.errors[0])

    def test_validate_empty_data_package(self):
        datapackage = {}
        schema = {
            'required': ['name'],
        }

        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(datapackage, schema)

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0], exceptions.ValidationError)


class TestValidateWithSchemaAsArgument(object):

    def setup_class(self):
        # a simple valid datapackage
        self.dp = (
            '{'
            '"name": "basic-data-package",'
            '"title": "Basic Data Package"'
            '}'
        )

    def test_schema_as_string(self):
        '''Pass schema as json string to validate()'''

        schema_dict = _get_local_base_datapackage_schema()
        datapackage_validate.validate(self.dp, schema_dict)

    def test_schema_as_wrong_object_type(self):
        '''Pass schema as not an expected object type (should be string or
        dict).'''

        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(self.dp, schema=123)

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0], exceptions.SchemaError)

    def test_schema_as_dict(self):
        '''Pass schema as python dict to validate()'''

        schema_dict = json.loads(_get_local_base_datapackage_schema())
        datapackage_validate.validate(self.dp, schema=schema_dict)

    @httpretty.activate
    def test_schema_as_valid_id(self):
        '''Pass schema as a valid string id to validate(). ID in registry.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        datapackage_validate.validate(self.dp, schema='base')

    @httpretty.activate
    def test_schema_as_invalid_id(self):
        '''Pass schema as an invalid string id to validate(). ID not in
        registry.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)

        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(self.dp, schema='not-a-valid-id')

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0], exceptions.SchemaError)

    @mock.patch('datapackage_registry.Registry')
    def test_raises_error_when_registry_raises_error(self, registry_mock):
        '''A 404 while getting the schema raises an error.'''
        registry_excep = datapackage_registry.exceptions
        registry_mock.side_effect = registry_excep.DataPackageRegistryException

        with pytest.raises(exceptions.DataPackageValidateException) as excinfo:
            datapackage_validate.validate(self.dp)

        assert excinfo.value.errors
        assert isinstance(excinfo.value.errors[0], exceptions.RegistryError)

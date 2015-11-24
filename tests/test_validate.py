from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import unittest

from nose.tools import (assert_true,
                        assert_is_instance,
                        assert_raises)
import httpretty

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


class TestValidDatapackageJson(unittest.TestCase):

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
        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(invalid_datapackage_json_str)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0],
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
        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(invalid_datapackage_json_str)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0],
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
        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(datapackage_obj)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.ValidationError)
        assert_true("'name' is a required property" in
                    str(cm.exception.errors[0]))

    def test_validate_empty_data_package(self):
        datapackage = {}
        schema = {
            'required': ['name'],
        }

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(datapackage, schema)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.ValidationError)


class TestValidateWithSchemaAsArgument(unittest.TestCase):

    '''Validate datapackage with a schema passed as an argument'''

    def setUp(self):
        # a simple valid datapackage
        self.dp = """{
  "name": "basic-data-package",
  "title": "Basic Data Package"
}"""

    def test_schema_as_string(self):
        '''Pass schema as json string to validate()'''

        schema_dict = _get_local_base_datapackage_schema()
        datapackage_validate.validate(self.dp, schema_dict)

    def test_schema_as_wrong_object_type(self):
        '''Pass schema as not an expected object type (should be string or
        dict).'''

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(self.dp, schema=123)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.SchemaError)

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

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(self.dp, schema='not-a-valid-id')

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.RegistryError)

    @httpretty.activate
    def test_schema_404_raises_error(self):
        '''A 404 while getting the schema raises an error.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body="404", status=404)

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(self.dp)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.RegistryError)

    @httpretty.activate
    def test_schema_500_raises_error(self):
        '''A 500 while getting the schema raises an error.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body="500", status=500)

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(self.dp)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.RegistryError)

    @httpretty.activate
    def test_registry_404_raises_error(self):
        '''A 404 while getting the registry raises an error.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body="404", status=404)

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(self.dp)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.RegistryError)

    @httpretty.activate
    def test_registry_500_raises_error(self):
        '''A 500 while getting the registry raises an error.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body="500", status=500)

        with assert_raises(exceptions.DataPackageValidateException) as cm:
            datapackage_validate.validate(self.dp)

        assert_true(cm.exception.errors)
        assert_is_instance(cm.exception.errors[0], exceptions.RegistryError)

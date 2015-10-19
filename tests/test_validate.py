from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import unittest

from nose.tools import (assert_true,
                        assert_false)
import httpretty

import datapackage_validate


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


class TestValidDatapackageJsonString(unittest.TestCase):

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
        valid, errors = datapackage_validate.validate(datapackage_json_str)

        assert_true(valid)
        assert_false(errors)

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
        valid, errors = datapackage_validate.validate(
            invalid_datapackage_json_str)

        assert_false(valid)
        assert_true(errors)
        assert_true('Invalid JSON:' in errors[0])

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
        valid, errors = datapackage_validate.validate(
            invalid_datapackage_json_str)

        assert_false(valid)
        assert_true(errors)
        assert_true('Invalid Data Package: not a string or object'
                    in errors[0])


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

        valid, errors = datapackage_validate.validate(
            self.dp, schema=_get_local_base_datapackage_schema())

        assert_true(valid)
        assert_false(errors)

    def test_schema_as_wrong_object_type(self):
        '''Pass schema as not an expected object type (should be string or
        dict).'''

        valid, errors = datapackage_validate.validate(
            self.dp, schema=123)

        assert_false(valid)
        assert_true(errors)
        assert_true('Invalid Schema: not a string or object'
                    in errors[0])

    def test_schema_as_dict(self):
        '''Pass schema as python dict to validate()'''

        schema_dict = json.loads(_get_local_base_datapackage_schema())

        valid, errors = datapackage_validate.validate(self.dp,
                                                      schema=schema_dict)

        assert_true(valid)
        assert_false(errors)

    @httpretty.activate
    def test_schema_as_valid_id(self):
        '''Pass schema as a valid string id to validate(). ID in registry.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        httpretty.register_uri(httpretty.GET,
                               'https://example.com/base_schema.json',
                               body=_get_local_base_datapackage_schema())

        valid, errors = datapackage_validate.validate(self.dp,
                                                      schema='base')

        assert_true(valid)
        assert_false(errors)

    @httpretty.activate
    def test_schema_as_invalid_id(self):
        '''Pass schema as an invalid string id to validate(). ID not in
        registry.'''
        httpretty.register_uri(httpretty.GET, REGISTRY_BACKEND_URL,
                               body=REGISTRY_BODY)
        valid, errors = datapackage_validate.validate(self.dp,
                                                      schema='not-a-valid-id')

        assert_false(valid)
        assert_true(errors)
        assert_true('Registry Error: no schema with id "not-a-valid-id"'
                    in errors[0])

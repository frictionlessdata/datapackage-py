# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import requests
import httpretty
from nose.tools import (assert_true,
                        assert_equal,
                        assert_raises)

import datapackage_registry


BACKEND_URL = "https://rawgit.com/dataprotocols/registry/master/registry.csv"


class TestRegistry(unittest.TestCase):

    @httpretty.activate
    def test_return_empty_array_when_registry_is_empty(self):
        '''Return an empty array when registry csv is empty'''
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="id,title,schema,specification")

        registry = datapackage_registry.Registry()
        assert_equal(registry.profiles, [],
                     'Registry is not an empty array')

    @httpretty.activate
    def test_return_non_empty_array_when_registry_is_not_empty(self):
        '''Return an array of dicts when registry csv is not empty'''

        body = """id,title,schema,specification
base,Data Package,https://example.com/one.json,http://example.com
tabular,Tabular Data Package,https://example.com/two.json,http://example.com"""

        httpretty.register_uri(httpretty.GET, BACKEND_URL, body=body)

        registry = datapackage_registry.Registry()

        assert_equal(len(registry.profiles), 2)
        # each member in array is a dict
        for profile in registry.profiles:
            assert_equal(type(profile), dict)

    @httpretty.activate
    def test_dicts_have_expected_keys(self):
        '''The returned dicts have the expected keys'''

        body = """id,title,schema,specification
base,Data Package,https://example.com/one.json,http://example.com
tabular,Tabular Data Package,https://example.com/two.json,http://example.com"""

        httpretty.register_uri(httpretty.GET, BACKEND_URL, body=body)

        registry = datapackage_registry.Registry()

        # each dict in array has the expected keys
        for profile in registry.profiles:
            assert_true('id' in profile)
            assert_true('title' in profile)
            assert_true('schema' in profile)
            assert_true('specification' in profile)

    @httpretty.activate
    def test_dicts_have_expected_values(self):
        '''The returned dicts have the expected values'''

        body = """id,title,schema,specification
base,Data Package,https://example.com/one.json,http://example.com
tabular,Tabular Data Package,https://example.com/two.json,http://example.com"""

        httpretty.register_uri(httpretty.GET, BACKEND_URL, body=body)

        registry = datapackage_registry.Registry()
        base_profile = registry.profiles[0]

        # first dict in array has the expected values
        assert_equal(base_profile['id'], 'base')
        assert_equal(base_profile['title'], 'Data Package')
        assert_equal(base_profile['schema'], 'https://example.com/one.json')
        assert_equal(base_profile['specification'], 'http://example.com')

    @httpretty.activate
    def test_custom_config_returns_expected_values(self):
        '''If a custom config is passed to get, return the appropriate values
        in the dict'''
        # default url has an empty csv file
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="id,title,schema,specification")
        custom_registry_url = 'http://example.com/custom_registry.csv'
        custom_body = """id,title,schema,specification
1,2,3,4
a,b,c,d"""

        # custom url has csv file with some rows we can test
        httpretty.register_uri(httpretty.GET,
                               custom_registry_url,
                               body=custom_body)

        custom_config = {
            'backend': custom_registry_url,
        }

        registry = datapackage_registry.Registry(custom_config)

        assert_equal(len(registry.profiles), 2)
        assert_equal(registry.profiles[0]['id'], '1')
        assert_equal(registry.profiles[0]['title'], '2')
        assert_equal(registry.profiles[0]['schema'], '3')
        assert_equal(registry.profiles[0]['specification'], '4')

    @httpretty.activate
    def test_unicode_in_registry(self):
        '''A utf-8 encoded string in the registry csv won't break the code.'''
        body = """id,title,schema,specification
base,Iñtërnâtiônàlizætiøn,3,4
a,b,c,d"""
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body=body)

        registry = datapackage_registry.Registry()

        assert_equal(len(registry.profiles), 2)
        assert_equal(registry.profiles[0]['id'], 'base')
        assert_equal(registry.profiles[0]['title'], 'Iñtërnâtiônàlizætiøn')

    @httpretty.activate
    def test_404_raises_error(self):
        '''A 404 while getting the registry raises an error.'''
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="404", status=404)

        with assert_raises(requests.HTTPError) as cm:
            datapackage_registry.Registry()
        assert_equal(cm.exception.response.status_code, 404)

    @httpretty.activate
    def test_500_raises_error(self):
        '''A 500 while getting the registry raises an error.'''
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="500", status=500)

        with assert_raises(requests.HTTPError) as cm:
            datapackage_registry.Registry()
        assert_equal(cm.exception.response.status_code, 500)

    def test_profiles_arent_writable(self):
        registry = datapackage_registry.Registry()
        with assert_raises(AttributeError):
            registry.profiles = ['foo']

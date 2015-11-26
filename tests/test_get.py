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


class DataPackageRegistryGetTest(unittest.TestCase):

    '''Tests for registry.get()'''

    @httpretty.activate
    def test_return_empty_dict_when_registry_is_empty(self):
        '''Return an empty dict when registry csv is empty'''
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="id,title,schema,specification")

        assert_equal(datapackage_registry.get(), {},
                     'Registry is not an empty dict')

    @httpretty.activate
    def test_return_non_empty_dict_when_registry_is_not_empty(self):
        '''Return an dict of dicts when registry csv is not empty'''

        body = """id,title,schema,specification
base,Data Package,https://example.com/one.json,http://example.com
tabular,Tabular Data Package,https://example.com/two.json,http://example.com"""

        httpretty.register_uri(httpretty.GET, BACKEND_URL, body=body)

        reg = datapackage_registry.get()
        assert_equal(len(reg), 2)
        # each profile in registry is a dict
        for o in reg.values():
            assert_equal(type(o), dict)

    @httpretty.activate
    def test_dicts_have_expected_keys(self):
        '''The returned profiles have the expected keys'''

        body = """id,title,schema,specification
base,Data Package,https://example.com/one.json,http://example.com
tabular,Tabular Data Package,https://example.com/two.json,http://example.com"""

        httpretty.register_uri(httpretty.GET, BACKEND_URL, body=body)

        reg = datapackage_registry.get()

        # each profile in registry has the expected keys
        for o in reg.values():
            assert_true('id' in o)
            assert_true('title' in o)
            assert_true('schema' in o)
            assert_true('specification' in o)

    @httpretty.activate
    def test_dicts_have_expected_values(self):
        '''The returned profiles have the expected values'''

        body = """id,title,schema,specification
base,Data Package,https://example.com/one.json,http://example.com
tabular,Tabular Data Package,https://example.com/two.json,http://example.com"""

        httpretty.register_uri(httpretty.GET, BACKEND_URL, body=body)

        reg = datapackage_registry.get()
        profile = reg['base']

        # first profile in registry has the expected values
        assert_equal(profile['id'], 'base')
        assert_equal(profile['title'], 'Data Package')
        assert_equal(profile['schema'], 'https://example.com/one.json')
        assert_equal(profile['specification'], 'http://example.com')

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

        reg = datapackage_registry.get(custom_config)
        profile = reg['1']
        assert_equal(len(reg), 2)
        assert_equal(profile['id'], '1')
        assert_equal(profile['title'], '2')
        assert_equal(profile['schema'], '3')
        assert_equal(profile['specification'], '4')

    @httpretty.activate
    def test_unicode_in_registry(self):
        '''A utf-8 encoded string in the registry csv won't break the code.'''
        body = """id,title,schema,specification
base,Iñtërnâtiônàlizætiøn,3,4
a,b,c,d"""
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body=body)

        reg = datapackage_registry.get()
        profile = reg['base']
        assert_equal(len(reg), 2)
        assert_equal(profile['id'], 'base')
        assert_equal(profile['title'], 'Iñtërnâtiônàlizætiøn')

    @httpretty.activate
    def test_404_raises_error(self):
        '''A 404 while getting the registry raises an error.'''
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="404", status=404)

        with assert_raises(requests.HTTPError) as cm:
            datapackage_registry.get()
        assert_equal(cm.exception.response.status_code, 404)

    @httpretty.activate
    def test_500_raises_error(self):
        '''A 500 while getting the registry raises an error.'''
        httpretty.register_uri(httpretty.GET, BACKEND_URL,
                               body="500", status=500)

        with assert_raises(requests.HTTPError) as cm:
            datapackage_registry.get()
        assert_equal(cm.exception.response.status_code, 500)

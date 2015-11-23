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

import tests.test_helpers as test_helpers
import datapackage_registry


class TestRegistry(unittest.TestCase):
    EMPTY_REGISTRY_PATH = test_helpers.fixture_path('empty_registry.csv')
    BASE_AND_TABULAR_REGISTRY_PATH = test_helpers.fixture_path('base_and_tabular_registry.csv')
    UNICODE_REGISTRY_PATH = test_helpers.fixture_path('unicode_registry.csv')

    def test_return_empty_array_when_registry_is_empty(self):
        '''Return an empty array when registry csv is empty'''
        config = {'backend': self.EMPTY_REGISTRY_PATH}
        registry = datapackage_registry.Registry(config)

        assert_equal(registry.profiles, [],
                     'Registry is not an empty array')

    def test_return_non_empty_array_when_registry_is_not_empty(self):
        '''Return an array of dicts when registry csv is not empty'''
        config = {'backend': self.BASE_AND_TABULAR_REGISTRY_PATH}
        registry = datapackage_registry.Registry(config)

        assert_equal(len(registry.profiles), 2)
        # each member in array is a dict
        for profile in registry.profiles:
            assert_equal(type(profile), dict)

    def test_dicts_have_expected_keys(self):
        '''The returned dicts have the expected keys'''
        config = {'backend': self.BASE_AND_TABULAR_REGISTRY_PATH}
        registry = datapackage_registry.Registry(config)

        # each dict in array has the expected keys
        for profile in registry.profiles:
            assert_true('id' in profile)
            assert_true('title' in profile)
            assert_true('schema' in profile)
            assert_true('specification' in profile)

    def test_dicts_have_expected_values(self):
        config = {'backend': self.BASE_AND_TABULAR_REGISTRY_PATH}
        registry = datapackage_registry.Registry(config)

        profile = registry.profiles[0]

        # first dict in array has the expected values
        assert_equal(profile['id'], 'base')
        assert_equal(profile['title'], 'Data Package')
        assert_equal(profile['schema'], 'http://example.com/one.json')
        assert_equal(profile['specification'], 'http://example.com')

    def test_unicode_in_registry(self):
        '''A utf-8 encoded string in the registry csv won't break the code.'''
        config = {'backend': self.UNICODE_REGISTRY_PATH}
        registry = datapackage_registry.Registry(config)

        assert_equal(len(registry.profiles), 2)
        assert_equal(registry.profiles[0]['id'], 'base')
        assert_equal(registry.profiles[0]['title'], 'Iñtërnâtiônàlizætiøn')

    @httpretty.activate
    def test_it_handles_remote_registry_files_over_http(self):
        '''It downloads remote registries when the backend is an URL.'''
        url = 'http://some-place.com/registry.csv'
        body = (
            'id,title,schema,specification\r\n'
            'base,Data Package,http://example.com/one.json,http://example.com'
        )
        httpretty.register_uri(httpretty.GET, url, body=body)

        config = {'backend': url}
        registry = datapackage_registry.Registry(config)

        assert_equal(len(registry.profiles), 1)
        profile = registry.profiles[0]
        assert_equal(profile['id'], 'base')
        assert_equal(profile['title'], 'Data Package')
        assert_equal(profile['schema'], 'http://example.com/one.json')
        assert_equal(profile['specification'], 'http://example.com')

    @httpretty.activate
    def test_404_raises_error(self):
        '''A 404 while getting the registry raises an error.'''
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url,
                               body="404", status=404)

        with assert_raises(requests.HTTPError) as cm:
            datapackage_registry.Registry({'backend': url})
        assert_equal(cm.exception.response.status_code, 404)

    @httpretty.activate
    def test_500_raises_error(self):
        '''A 500 while getting the registry raises an error.'''
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url,
                               body="500", status=500)

        with assert_raises(requests.HTTPError) as cm:
            datapackage_registry.Registry({'backend': url})
        assert_equal(cm.exception.response.status_code, 500)

    def test_profiles_arent_writable(self):
        registry = datapackage_registry.Registry()
        with assert_raises(AttributeError):
            registry.profiles = ['foo']

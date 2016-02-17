# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

try:
    import mock
except ImportError:
    import unittest.mock as mock

import os
import pytest
import httpretty
import tests.test_helpers as test_helpers
import datapackage.registry
from datapackage.exceptions import RegistryError


class TestRegistry(object):
    EMPTY_REGISTRY_PATH = test_helpers.fixture_path('empty_registry.csv')
    BASE_AND_TABULAR_REGISTRY_PATH = test_helpers.fixture_path('base_and_tabular_registry.csv')
    UNICODE_REGISTRY_PATH = test_helpers.fixture_path('unicode_registry.csv')
    BASE_PROFILE_PATH = test_helpers.fixture_path('base_profile.json')

    def test_return_empty_dict_when_registry_is_empty(self):
        '''Return an empty dict when registry csv is empty'''
        registry_path = self.EMPTY_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert registry.available_profiles == {}

    def test_return_non_empty_dict_when_registry_is_not_empty(self):
        '''Return an dict of dicts when registry csv is not empty'''
        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert len(registry.available_profiles) == 2
        # each member in dict is a dict
        for profile in registry.available_profiles.values():
            assert type(profile) == dict

    def test_dicts_have_expected_keys(self):
        '''The returned dicts have the expected keys'''
        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        # each dict in profiles has the expected keys
        for profile in registry.available_profiles.values():
            assert sorted(profile.keys()) == \
                   sorted(['id', 'title', 'schema', 'schema_path', 'specification'])

    def test_dicts_have_expected_values(self):
        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert len(registry.available_profiles) == 2

        # base profile has the expected values
        assert registry.available_profiles.get('base') == {
            'id': 'base',
            'title': 'Data Package',
            'schema': 'http://example.com/one.json',
            'schema_path': 'base_profile.json',
            'specification': 'http://example.com',
        }

    def test_unicode_in_registry(self):
        '''A utf-8 encoded string in the registry csv won't break the code.'''
        registry_path = self.UNICODE_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert len(registry.available_profiles) == 2
        base_profile_metadata = registry.available_profiles.get('base')
        assert base_profile_metadata['id'] == 'base'
        assert base_profile_metadata['title'] == 'Iñtërnâtiônàlizætiøn'

    @httpretty.activate
    def test_it_handles_remote_registry_files_over_http(self):
        '''It downloads remote registries when the backend is an URL.'''
        url = 'http://some-place.com/registry.csv'
        body = (
            'id,title,schema,specification\r\n'
            'base,Data Package,http://example.com/one.json,http://example.com'
        )
        httpretty.register_uri(httpretty.GET, url, body=body)

        registry = datapackage.registry.Registry(url)

        assert len(registry.available_profiles) == 1
        assert registry.available_profiles.get('base') == {
            'id': 'base',
            'title': 'Data Package',
            'schema': 'http://example.com/one.json',
            'specification': 'http://example.com',
        }

    @httpretty.activate
    def test_raises_error_if_registry_has_no_id_field(self):
        '''A 404 while getting the registry raises an error.'''
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url,
                               body="foo\nbar")

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    @httpretty.activate
    def test_404_raises_error(self):
        '''A 404 while getting the registry raises an error.'''
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url,
                               body="404", status=404)

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    @httpretty.activate
    def test_500_raises_error(self):
        '''A 500 while getting the registry raises an error.'''
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url,
                               body="500", status=500)

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    @httpretty.activate
    def test_raises_if_profile_in_remote_file_isnt_a_json(self):
        url = 'http://some-place.com/registry.csv'
        body = (
            'id,schema\r\n'
            'notajson,http://example.com/one.json'
        )
        httpretty.register_uri(httpretty.GET, url, body=body)
        httpretty.register_uri(httpretty.GET, 'http://example.com/one.json',
                               body='I\'m not a JSON')

        registry = datapackage.registry.Registry(url)

        with pytest.raises(RegistryError):
            registry.get('notajson')

    def test_raises_if_profile_in_local_file_isnt_a_json(self):
        registry_path = test_helpers.fixture_path('registry_with_notajson_profile.csv')
        registry = datapackage.registry.Registry(registry_path)

        with pytest.raises(RegistryError):
            registry.get('notajson')

    def test_available_profiles_arent_writable(self):
        registry = datapackage.registry.Registry()
        with pytest.raises(AttributeError):
            registry.available_profiles = {}

    @httpretty.activate
    def test_get_loads_available_profile_from_disk(self):
        httpretty.HTTPretty.allow_net_connect = False

        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        base_profile = registry.get('base')
        assert base_profile is not None
        assert base_profile['title'] == 'base_profile'

    @httpretty.activate
    def test_get_loads_file_from_http_if_theres_no_local_copy(self):
        registry_url = 'http://some-place.com/registry.csv'
        registry_body = (
            'id,title,schema,specification\r\n'
            'base,Data Package,http://example.com/one.json,http://example.com'
        )
        httpretty.register_uri(httpretty.GET, registry_url, body=registry_body)

        profile_url = 'http://example.com/one.json'
        profile_body = '{ "title": "base_profile" }'
        httpretty.register_uri(httpretty.GET, profile_url, body=profile_body)

        registry = datapackage.registry.Registry(registry_url)

        base_profile = registry.get('base')
        assert base_profile is not None
        assert base_profile == {'title': 'base_profile'}

    @httpretty.activate
    def test_get_loads_file_from_http_if_local_copys_path_isnt_a_file(self):
        registry_url = 'http://some-place.com/registry.csv'
        registry_body = (
            'id,title,schema,specification,schema_path\r\n'
            'base,Data Package,http://example.com/one.json,http://example.com,inexistent.json'
        )
        httpretty.register_uri(httpretty.GET, registry_url, body=registry_body)

        profile_url = 'http://example.com/one.json'
        profile_body = '{ "title": "base_profile" }'
        httpretty.register_uri(httpretty.GET, profile_url, body=profile_body)

        registry = datapackage.registry.Registry(registry_url)

        base_profile = registry.get('base')
        assert base_profile is not None
        assert base_profile == {'title': 'base_profile'}

    def test_get_returns_none_if_profile_doesnt_exist(self):
        registry = datapackage.registry.Registry()
        assert registry.get('non-existent-profile') is None

    def test_get_memoize_the_profiles(self):
        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        registry.get('base')

        m = mock.mock_open(read_data='{}')
        with mock.patch('datapackage.registry.open', m):
            registry.get('base')

        assert not m.called, '.get() should memoize the profiles'

    def test_base_path_default(self):
        registry = datapackage.registry.Registry()
        base_path = os.path.dirname(registry.DEFAULT_REGISTRY_PATH)

        assert registry.base_path == base_path

    def test_base_path_uses_received_registry_base_path(self):
        registry = datapackage.registry.Registry(self.EMPTY_REGISTRY_PATH)
        base_path = os.path.dirname(self.EMPTY_REGISTRY_PATH)

        assert registry.base_path == base_path

    @httpretty.activate
    def test_base_path_is_none_if_registry_is_remote(self):
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url, body='')
        registry = datapackage.registry.Registry(url)

        assert registry.base_path is None

    @httpretty.activate
    def test_base_path_cant_be_set(self):
        registry = datapackage.registry.Registry()

        with pytest.raises(AttributeError):
            registry.base_path = '/another/path'

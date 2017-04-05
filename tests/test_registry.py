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
import tempfile
import tests.test_helpers as test_helpers
import datapackage.registry
from datapackage.exceptions import RegistryError


class TestRegistry(object):
    EMPTY_REGISTRY_PATH = test_helpers.fixture_path('empty_registry.json')
    BASE_AND_TABULAR_REGISTRY_PATH = test_helpers.fixture_path('base_and_tabular_registry.json')
    UNICODE_REGISTRY_PATH = test_helpers.fixture_path('unicode_registry.json')
    BASE_PROFILE_PATH = test_helpers.fixture_path('base_profile.json')

    @httpretty.activate
    def test_init_accepts_urls(self):
        url = 'http://some-place.com/registry.json'
        body = """
        [
          {
            "id": "data-package",
            "title": "Data Package",
            "schema": "https://specs.frictionlessdata.io/schemas/data-package.json",
            "schema_path": "data-package.json",
            "specification": "https://specs.frictionlessdata.io/data-package/"
          }
        ]
        """
        httpretty.register_uri(httpretty.GET, url, body=body)

        registry = datapackage.registry.Registry(url)

        assert len(registry.available_profiles) == 1
        assert registry.available_profiles.get('data-package') == {
            'id': 'data-package',
            'title': 'Data Package',
            'schema': 'https://specs.frictionlessdata.io/schemas/data-package.json',
            'schema_path': 'data-package.json',
            'specification': 'https://specs.frictionlessdata.io/data-package/',
        }

    @httpretty.activate
    def test_init_raises_if_registry_isnt_a_csv(self):
        url = 'http://some-place.com/registry.txt'
        httpretty.register_uri(httpretty.GET, url,
                               body="foo")

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    @httpretty.activate
    def test_init_raises_if_registry_has_no_id_field(self):
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url,
                               body="foo\nbar")

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    @httpretty.activate
    def test_init_raises_if_registry_url_doesnt_exist(self):
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url, status=404)

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    @httpretty.activate
    def test_init_raises_if_registry_url_webserver_raises_error(self):
        url = 'http://some-place.com/registry.csv'
        httpretty.register_uri(httpretty.GET, url, status=500)

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(url)

    def test_init_raises_if_registry_path_doesnt_exist(self):
        registry_path = 'inexistent-registry-path.csv'

        with pytest.raises(RegistryError):
            datapackage.registry.Registry(registry_path)

    def test_it_has_default_registry_url_const(self):
        url = 'https://specs.frictionlessdata.io/specs/registry.json'
        assert datapackage.registry.Registry.DEFAULT_REGISTRY_URL == url

    def test_available_profiles_returns_empty_dict_when_registry_is_empty(self):
        registry_path = self.EMPTY_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert registry.available_profiles == {}

    def test_available_profiles_returns_list_of_profiles_dicts(self):
        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert len(registry.available_profiles) == 2
        assert registry.available_profiles.get('data-package') == {
            'id': 'data-package',
            'title': 'Data Package',
            'schema': 'https://specs.frictionlessdata.io/schemas/data-package.json',
            'schema_path': 'data-package.json',
            'specification': 'https://specs.frictionlessdata.io/data-package/',
        }
        assert registry.available_profiles.get('tabular-data-package') == {
            'id': 'tabular-data-package',
            'title': 'Tabular Data Package',
            'schema': 'https://specs.frictionlessdata.io/schemas/tabular-data-package.json',
            'schema_path': 'tabular-data-package.json',
            'specification': 'http://specs.frictionlessdata.io/tabular-data-package/',
        }

    def test_available_profiles_cant_be_set(self):
        registry = datapackage.registry.Registry()
        with pytest.raises(AttributeError):
            registry.available_profiles = {}

    def test_available_profiles_works_with_unicode_strings_in_registry(self):
        registry_path = self.UNICODE_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        assert len(registry.available_profiles) == 2
        base_profile_metadata = registry.available_profiles.get('unicode-data-package')
        assert base_profile_metadata['title'] == 'Iñtërnâtiônàlizætiøn'

    @httpretty.activate
    def test_get_loads_profile_from_disk(self):
        httpretty.HTTPretty.allow_net_connect = False

        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        base_profile = registry.get('data-package')
        assert base_profile is not None
        assert base_profile['profile'] == 'data-package'

    @httpretty.activate
    def test_get_loads_remote_file_if_local_copy_doesnt_exist(self):
        registry_body = """
        [
          {
            "id": "data-package",
            "title": "Data Package",
            "schema": "http://example.com/one.json",
            "schema_path": "data-package.json",
            "specification": "https://specs.frictionlessdata.io/data-package/"
          }
        ]
        """
        profile_url = 'http://example.com/one.json'
        profile_body = '{ "profile": "data-package" }'
        httpretty.register_uri(httpretty.GET, profile_url, body=profile_body)

        with tempfile.NamedTemporaryFile(suffix='.csv') as tmpfile:
            tmpfile.write(registry_body.encode('utf-8'))
            tmpfile.flush()

            registry = datapackage.registry.Registry(tmpfile.name)

        base_profile = registry.get('data-package')
        assert base_profile is not None
        assert base_profile == {'profile': 'data-package'}

    def test_get_raises_if_profile_isnt_a_json(self):
        registry_path = test_helpers.fixture_path('registry_with_notajson_profile.json')
        registry = datapackage.registry.Registry(registry_path)

        with pytest.raises(RegistryError):
            registry.get('notajson-data-package')

    @httpretty.activate
    def test_get_raises_if_remote_profile_file_doesnt_exist(self):
        registry_url = 'http://example.com/registry.json'
        registry_body = """
        [
          {
            "id": "data-package",
            "title": "Data Package",
            "schema": "http://example.com/one.json",
            "schema_path": "data-package.json",
            "specification": "http://example.com"
          }
        ]
        """
        httpretty.register_uri(httpretty.GET, registry_url, body=registry_body)
        profile_url = 'http://example.com/one.json'
        httpretty.register_uri(httpretty.GET, profile_url, status=404)

        registry = datapackage.registry.Registry(registry_url)

        with pytest.raises(RegistryError):
            registry.get('data-package')

    @httpretty.activate
    def test_get_raises_if_local_profile_file_doesnt_exist(self):
        registry_body = """
        [
          {
            "id": "data-package",
            "title": "Data Package",
            "schema": "http://example.com/one.json",
            "schema_path": "inexistent.json",
            "specification": "http://example.com"
          }
        ]
        """
        with tempfile.NamedTemporaryFile(suffix='.csv') as tmpfile:
            tmpfile.write(registry_body.encode('utf-8'))
            tmpfile.flush()

            registry = datapackage.registry.Registry(tmpfile.name)

        profile_url = 'http://example.com/one.json'
        httpretty.register_uri(httpretty.GET, profile_url, status=404)

        with pytest.raises(RegistryError):
            registry.get('data-package')

    def test_get_returns_none_if_profile_doesnt_exist(self):
        registry = datapackage.registry.Registry()
        assert registry.get('non-existent-profile') is None

    def test_get_memoize_the_profiles(self):
        registry_path = self.BASE_AND_TABULAR_REGISTRY_PATH
        registry = datapackage.registry.Registry(registry_path)

        registry.get('data-package')

        m = mock.mock_open(read_data='{}')
        with mock.patch('datapackage.registry.open', m):
            registry.get('data-package')

        assert not m.called, '.get() should memoize the profiles'

    def test_base_path_defaults_to_the_local_cache_path(self):
        registry = datapackage.registry.Registry()
        base_path = os.path.dirname(registry.DEFAULT_REGISTRY_PATH)

        assert registry.base_path == base_path

    def test_base_path_uses_received_registry_base_path(self):
        registry = datapackage.registry.Registry(self.EMPTY_REGISTRY_PATH)
        base_path = os.path.dirname(self.EMPTY_REGISTRY_PATH)

        assert registry.base_path == base_path

    @httpretty.activate
    def test_base_path_is_none_if_registry_is_remote(self):
        url = 'http://some-place.com/registry.json'
        httpretty.register_uri(httpretty.GET, url, body='[]')
        registry = datapackage.registry.Registry(url)

        assert registry.base_path is None

    @httpretty.activate
    def test_base_path_cant_be_set(self):
        registry = datapackage.registry.Registry()

        with pytest.raises(AttributeError):
            registry.base_path = '/another/path'

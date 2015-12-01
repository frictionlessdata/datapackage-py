 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest
import httpretty
import tests.test_helpers as test_helpers
import datapackage
import datapackage.resource
import datapackage.exceptions

TabularResource = datapackage.resource.TabularResource


class TestResource(object):
    def test_metadata_are_available(self):
        resource_dict = {
            'name': 'foo',
            'url': 'http://someplace.com/foo.json',
            'path': 'foo.json',
            'data': {'foo': 'bar'},
        }
        resource = datapackage.Resource(resource_dict)
        assert resource.metadata == resource_dict

    def test_metadata_cant_be_assigned(self):
        resource_dict = {}
        resource = datapackage.Resource(resource_dict)
        with pytest.raises(AttributeError):
            resource.metadata = {}

    def test_data_is_none_by_default(self):
        resource_dict = {}
        resource = datapackage.Resource(resource_dict)
        assert resource.data is None

    def test_data_returns_the_resource_data(self):
        resource_dict = {
            'data': 'foo',
        }
        resource = datapackage.Resource(resource_dict)
        assert resource.data == resource_dict['data']

    def test_data_cant_be_assigned(self):
        resource_dict = {}
        resource = datapackage.Resource(resource_dict)
        with pytest.raises(AttributeError):
            resource.data = 'foo'

    def test_load_inline_string(self):
        resource_dict = {
            'data': '万事开头难'
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == resource_dict['data']

    def test_load_inline_number(self):
        resource_dict = {
            'data': 51
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == resource_dict['data']

    def test_load_tabular_data_returns_tabularresource_instance(self):
        resource_dict = {
            'data': [
                {'country': 'China', 'value': '中国'},
                {'country': 'Brazil', 'value': 'Brasil'}
            ],
        }
        resource = datapackage.Resource.load(resource_dict)
        assert isinstance(resource, TabularResource)

    def test_load_prefers_loading_inline_data_over_path_and_url(self):
        resource_dict = {
            'data': [
                {'country': 'China', 'value': '中国'},
                {'country': 'Brazil', 'value': 'Brasil'}
            ],
            'path': 'inexistent-file.json',
            'url': 'http://someplace.com/inexistent-file.json',
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == resource_dict['data']

    @httpretty.activate
    def test_load_prefers_loading_local_data_over_url(self):
        httpretty.HTTPretty.allow_net_connect = False
        resource_dict = {
            'path': test_helpers.fixture_path('unicode.txt'),
            'url': 'http://someplace.com/inexistent-file.json',
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == '万事开头难\n'

    @httpretty.activate
    def test_load_loads_from_url_if_local_path_doesnt_exist(self):
        httpretty.HTTPretty.allow_net_connect = False
        base_url = 'http://someplace.com'
        path = 'resource.txt'
        url = '{base_url}/{path}'.format(base_url=base_url, path=path)
        body = '万事开头难'
        httpretty.register_uri(httpretty.GET, url, body=body)
        httpretty.register_uri(httpretty.GET,
                               '{0}/nonexistent-file.txt'.format(base_url),
                               status=404)

        resource_dict = {
            'path': 'nonexistent-file.txt',
            'url': url
        }

        resource = datapackage.Resource.load(resource_dict,
                                             default_base_path=base_url)
        assert resource.data == body

    @httpretty.activate
    def test_load_accepts_url(self):
        url = 'http://someplace/resource.txt'
        body = '万事开头难'
        httpretty.register_uri(httpretty.GET, url, body=body)

        resource_dict = {
            'url': url,
        }

        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == body

    @httpretty.activate
    def test_load_raises_if_url_doesnt_exist(self):
        url = 'http://someplace/resource.txt'
        httpretty.register_uri(httpretty.GET, url, status=404)

        resource_dict = {
            'url': url,
        }

        with pytest.raises(datapackage.exceptions.ResourceError):
            datapackage.Resource.load(resource_dict)

    def test_load_accepts_absolute_paths(self):
        path = test_helpers.fixture_path('unicode.txt')
        resource_dict = {
            'path': path,
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == '万事开头难\n'

    def test_load_accepts_relative_paths(self):
        filename = 'unicode.txt'
        base_path = os.path.dirname(
            test_helpers.fixture_path(filename)
        )
        resource_dict = {
            'path': filename,
        }
        resource = datapackage.Resource.load(resource_dict, base_path)
        assert resource.data == '万事开头难\n'

    def test_load_accepts_relative_paths_with_base_defined_in_metadata(self):
        filename = 'unicode.txt'
        base_path = os.path.dirname(
            test_helpers.fixture_path(filename)
        )
        resource_dict = {
            'path': filename,
            'base': base_path,
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == '万事开头难\n'

    def test_load_base_path_in_metadata_overloads_base_passed_in_args(self):
        filename = 'unicode.txt'
        base_path = os.path.dirname(
            test_helpers.fixture_path(filename)
        )
        resource_dict = {
            'path': filename,
            'base': base_path,
        }
        resource = datapackage.Resource.load(resource_dict,
                                             'invalid_base_path')
        assert resource.data == '万事开头难\n'

    @httpretty.activate
    def test_load_accepts_relative_urls(self):
        base_url = 'http://someplace.com'
        path = 'resource.txt'
        url = '{base_url}/{path}'.format(base_url=base_url, path=path)
        body = '万事开头难'
        httpretty.register_uri(httpretty.GET, url, body=body)

        resource_dict = {
            'path': path,
        }

        resource = datapackage.Resource.load(resource_dict,
                                             default_base_path=base_url)
        assert resource.data == body

    def test_load_raises_if_path_doesnt_exist(self):
        resource_dict = {
            'path': 'inexistent-file.json',
        }

        with pytest.raises(datapackage.exceptions.ResourceError):
            datapackage.Resource.load(resource_dict)

    def test_can_change_data_path_after_creation(self):
        original_path = test_helpers.fixture_path('unicode.txt')
        new_path = test_helpers.fixture_path('foo.txt')
        resource_dict = {
            'path': original_path
        }
        resource = datapackage.Resource.load(resource_dict)
        resource.metadata['path'] = new_path
        assert resource.data == 'foo\n'

    @httpretty.activate
    def test_can_change_data_url_after_creation(self):
        original_url = 'http://someplace.com/foo.txt'
        original_body = 'foo'
        httpretty.register_uri(httpretty.GET, original_url,
                               body=original_body)
        new_url = 'http://someplace.com/bar.txt'
        new_body = 'bar'
        httpretty.register_uri(httpretty.GET, new_url,
                               body=new_body)

        resource_dict = {
            'url': original_url
        }
        resource = datapackage.Resource.load(resource_dict)
        resource.metadata['url'] = new_url
        assert resource.data == new_body

    def test_can_change_the_data_after_creation(self):
        resource_dict = {
            'data': ['foo']
        }
        resource = datapackage.Resource.load(resource_dict)
        resource.metadata['data'] = ['bar']
        assert resource.data == ['bar']


class TestTabularResource(object):
    def test_load_inline_list(self):
        resource_dict = {
            'data': [
                {'country': 'China', 'value': '中国'},
                {'country': 'Brazil', 'value': 'Brasil'}
            ],
        }
        resource = TabularResource(resource_dict)
        assert resource.data == resource_dict['data']

    def test_load_inline_csv(self):
        resource_dict = {
            'data': (
                'country,value\r\n'
                'China,中国\r\n'
                'Brazil,Brasil\r\n'
            )
        }
        resource = TabularResource(resource_dict)
        assert len(resource.data) == 2
        assert resource.data[0] == {'country': 'China', 'value': '中国'}
        assert resource.data[1] == {'country': 'Brazil', 'value': 'Brasil'}

    def test_load_inline_json(self):
        resource_dict = {
            'data': (
                '['
                '{"country": "China", "value": "中国"},'
                '{"country": "Brazil", "value": "Brasil"}'
                ']'
            )
        }
        resource = TabularResource(resource_dict)
        assert len(resource.data) == 2
        assert resource.data[0] == {'country': 'China', 'value': '中国'}
        assert resource.data[1] == {'country': 'Brazil', 'value': 'Brasil'}

    @httpretty.activate
    def test_load_url(self):
        url = 'http://someplace/resource.json'
        body = (
            '['
            '{"country": "China", "value": "中国"},'
            '{"country": "Brazil", "value": "Brasil"}'
            ']'
        )
        httpretty.register_uri(httpretty.GET, url,
                               body=body, content_type='application/json')

        resource_dict = {
            'url': url,
        }

        resource = TabularResource(resource_dict)
        assert len(resource.data) == 2
        assert resource.data[0] == {'country': 'China', 'value': '中国'}
        assert resource.data[1] == {'country': 'Brazil', 'value': 'Brasil'}

    def test_raises_valueerror_if_data_is_dict(self):
        resource_dict = {
            'data': {
                'foo': 'bar',
            },
        }

        with pytest.raises(ValueError):
            TabularResource(resource_dict)

    def test_raises_valueerror_if_data_is_number(self):
        resource_dict = {
            'data': 51,
        }
        with pytest.raises(ValueError):
            TabularResource(resource_dict)

    def test_raises_valueerror_if_data_is_none(self):
        resource_dict = {
            'data': None,
        }
        with pytest.raises(ValueError):
            TabularResource(resource_dict)

    def test_raises_valueerror_if_theres_no_data(self):
        resource_dict = {}
        with pytest.raises(ValueError):
            TabularResource(resource_dict)

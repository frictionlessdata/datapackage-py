 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import datapackage
import datapackage.resource

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

    def test_load_inline_dict(self):
        resource_dict = {
            'data': {
                'country': 'China',
                'value': '中国',
            },
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

    def test_load_prefers_loading_inline_data_over_path_and_url(self):
        resource_dict = {
            'data': [
                {'country': 'China', 'value': '中国'},
                {'country': 'Brazil', 'value': 'Brasil'}
            ],
            'path': 'data.json',
            'url': 'http://someplace.com/data.json',
        }
        resource = TabularResource(resource_dict)
        assert resource.data == resource_dict['data']

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

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
    def test_descriptor_are_available(self):
        resource_dict = {
            'name': 'foo',
            'url': 'http://someplace.com/foo.json',
            'path': 'foo.json',
            'data': {'foo': 'bar'},
        }
        resource = datapackage.Resource(resource_dict)
        assert resource.descriptor == resource_dict

    def test_descriptor_cant_be_assigned(self):
        resource_dict = {}
        resource = datapackage.Resource(resource_dict)
        with pytest.raises(AttributeError):
            resource.descriptor = {}

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

    @httpretty.activate
    def test_data_is_lazily_loaded(self):
        httpretty.HTTPretty.allow_net_connect = False
        resource_dict = {
            'url': 'http://someplace.com/somefile.txt',
        }
        resource = datapackage.Resource.load(resource_dict)

        httpretty.register_uri(httpretty.GET, resource_dict['url'], body='foo')

        assert resource.data == b'foo'

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
            'path': test_helpers.fixture_path('foo.txt'),
            'url': 'http://someplace.com/inexistent-file.txt',
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == b'foo\n'

    @httpretty.activate
    def test_load_loads_from_url_if_local_path_doesnt_exist(self):
        httpretty.HTTPretty.allow_net_connect = False
        base_url = 'http://someplace.com'
        path = 'resource.txt'
        url = '{base_url}/{path}'.format(base_url=base_url, path=path)
        httpretty.register_uri(httpretty.GET, url, body='foo')
        httpretty.register_uri(httpretty.GET,
                               '{0}/nonexistent-file.txt'.format(base_url),
                               status=404)

        resource_dict = {
            'path': 'nonexistent-file.txt',
            'url': url
        }

        resource = datapackage.Resource.load(resource_dict,
                                             default_base_path=base_url)
        assert resource.data == b'foo'

    @httpretty.activate
    def test_load_accepts_url(self):
        url = 'http://someplace/resource.txt'
        httpretty.register_uri(httpretty.GET, url, body='foo')

        resource_dict = {
            'url': url,
        }

        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == b'foo'

    def test_load_accepts_absolute_paths(self):
        path = test_helpers.fixture_path('foo.txt')
        resource_dict = {
            'path': path,
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.data == b'foo\n'

    def test_load_accepts_relative_paths(self):
        filename = 'foo.txt'
        base_path = os.path.dirname(
            test_helpers.fixture_path(filename)
        )
        resource_dict = {
            'path': filename,
        }
        resource = datapackage.Resource.load(resource_dict, base_path)
        assert resource.data == b'foo\n'

    def test_load_binary_data(self):
        resource_dict = {
            'path': test_helpers.fixture_path('image.gif'),
        }
        resource = datapackage.Resource.load(resource_dict)

        with open(resource_dict['path'], 'rb') as f:
            assert resource.data == f.read()

    @httpretty.activate
    def test_load_accepts_relative_urls(self):
        base_url = 'http://someplace.com'
        path = 'resource.txt'
        url = '{base_url}/{path}'.format(base_url=base_url, path=path)
        httpretty.register_uri(httpretty.GET, url, body='foo')

        resource_dict = {
            'path': path,
        }

        resource = datapackage.Resource.load(resource_dict,
                                             default_base_path=base_url)
        assert resource.data == b'foo'

    @httpretty.activate
    def test_data_raises_if_url_doesnt_exist(self):
        url = 'http://someplace/resource.txt'
        httpretty.register_uri(httpretty.GET, url, status=404)

        resource_dict = {
            'url': url,
        }

        with pytest.raises(IOError):
            datapackage.Resource.load(resource_dict).data

    def test_data_raises_if_path_doesnt_exist(self):
        resource_dict = {
            'path': 'inexistent-file.json',
        }

        with pytest.raises(IOError):
            datapackage.Resource.load(resource_dict).data

    def test_can_change_data_path_after_creation(self):
        original_path = test_helpers.fixture_path('unicode.txt')
        new_path = test_helpers.fixture_path('foo.txt')
        resource_dict = {
            'path': original_path
        }
        resource = datapackage.Resource.load(resource_dict)
        resource.descriptor['path'] = new_path
        assert resource.data == b'foo\n'

    @httpretty.activate
    def test_can_change_data_url_after_creation(self):
        original_url = 'http://someplace.com/foo.txt'
        httpretty.register_uri(httpretty.GET, original_url,
                               body='foo')
        new_url = 'http://someplace.com/bar.txt'
        httpretty.register_uri(httpretty.GET, new_url,
                               body='bar')

        resource_dict = {
            'url': original_url
        }
        resource = datapackage.Resource.load(resource_dict)
        resource.descriptor['url'] = new_url
        assert resource.data == b'bar'

    def test_can_change_the_data_after_creation(self):
        resource_dict = {
            'data': ['foo']
        }
        resource = datapackage.Resource.load(resource_dict)
        resource.descriptor['data'] = ['bar']
        assert resource.data == ['bar']

    def test_local_data_path_returns_the_unmodified_path(self):
        resource_dict = {
            'path': test_helpers.fixture_path('unicode.txt'),
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.local_data_path == resource_dict['path']

    def test_local_data_path_returns_the_absolute_path(self):
        base_path = test_helpers.fixture_path('')
        path = os.path.join(base_path, '..', 'fixtures', 'unicode.txt')
        resource_dict = {
            'path': path,
        }
        resource = datapackage.Resource.load(resource_dict)
        abs_path = os.path.join(base_path, 'unicode.txt')
        assert resource.local_data_path == abs_path

    def test_local_data_path_returns_none_if_theres_no_file(self):
        resource_dict = {
            'data': 'foo',
            'url': 'http://someplace.com/foo.txt'
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.local_data_path is None

    def test_local_data_path_returns_abs_path_even_if_it_doesnt_exist(self):
        path = 'nonexistent.csv'
        resource_dict = {
            'data': 'foo',  # Avoid throwing error because path doesn't exist
            'path': path,
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.local_data_path == os.path.abspath(path)

    def test_remote_data_path_returns_the_unmodified_url(self):
        resource_dict = {
            'url': 'http://somewhere.com/data.txt',
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.remote_data_path == resource_dict['url']

    def test_remote_data_path_returns_none_if_theres_no_remote_data(self):
        resource_dict = {
            'data': 'foo',
            'path': test_helpers.fixture_path('unicode.txt'),
        }
        resource = datapackage.Resource.load(resource_dict)
        assert resource.remote_data_path is None

    def test_iterator_with_inline_data(self):
        contents = (
            'first line\n'
            'second line\n'
        )
        resource = datapackage.Resource.load({'data': contents})

        data = [row for row in resource.iter()]
        assert data == [b'first line\n', b'second line\n']

    def test_iterator_with_inline_numerical_data(self):
        contents = 51
        resource = datapackage.Resource.load({'data': contents})

        assert [row for row in resource.iter()] == [51]

    def test_iterator_with_local_data(self, txt_tmpfile):
        contents = (
            'first line\n'
            'second line\n'
        )

        txt_tmpfile.write(contents.encode('utf-8'))
        txt_tmpfile.flush()
        resource = datapackage.Resource.load({'path': txt_tmpfile.name})
        data = [row for row in resource.iter()]

        assert data == [b'first line\n', b'second line\n']

    @httpretty.activate
    def test_iterator_with_remote_data(self):
        httpretty.HTTPretty.allow_net_connect = False
        contents = (
            'first line\n'
            'second line\n'
        )
        resource_dict = {
            'url': 'http://someplace.com/data.txt',
        }
        httpretty.register_uri(httpretty.GET, resource_dict['url'],
                               body=contents)

        resource = datapackage.Resource.load(resource_dict)

        data = [row for row in resource.iter()]
        assert data == [b'first line\n', b'second line\n']

    def test_iterator_raises_valueerror_if_theres_no_data(self):
        resource = datapackage.Resource.load({})
        with pytest.raises(ValueError):
            [row for row in resource.iter()]

    def test_iterator_raises_if_file_doesnt_exist(self):
        resource = datapackage.Resource.load({'path': 'inexistent-file.txt'})
        with pytest.raises(IOError):
            [row for row in resource.iter()]

    @httpretty.activate
    def test_iterator_raises_resourceerror_if_url_doesnt_exist(self):
        url = 'http://someplace.com/inexistent-file.txt'
        httpretty.register_uri(httpretty.GET, url, status=404)
        resource = datapackage.Resource.load({'url': url})
        with pytest.raises(IOError):
            [row for row in resource.iter()]


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

    def test_load_tsv(self):
        resource_dict = {
            'path': test_helpers.fixture_path('cities.tsv')
        }

        resource = TabularResource(resource_dict)
        assert resource.data == [
            {'Area': '1807.92', 'Name': 'Acrelândia', 'Population': '12538', 'State': 'AC'},
            {'Area': '186.53', 'Name': 'Boca da Mata', 'Population': '25776', 'State': 'AL'},
            {'Area': '242.62', 'Name': 'Capela', 'Population': '17077', 'State': 'AL'},
            {'Area': '6709.66', 'Name': 'Tartarugalzinho', 'Population': '12563', 'State': 'AP'},
            {'Area': '837.72', 'Name': 'América Dourada', 'Population': None, 'State': 'BA'},
            {'Area': '204.79', 'Name': 'Jijoca de Jericoacoara', 'Population': '17002', 'State': 'CE'},
            {'Area': '6953.67', 'Name': 'Cavalcante', 'Population': '9392', 'State': 'GO'},
            {'Area': '8258.42', 'Name': 'Centro Novo do Maranhão', 'Population': '17622', 'State': 'MA'},
            {'Area': '3651.18', 'Name': 'Ped\\ro G\\omes', 'Population': '7967', 'State': 'MS'},
            {'Area': '881.06', 'Name': 'Abadia dos Dourados', 'Population': '6704', 'State': 'MG'},
        ]

    def test_accepts_urls_with_query_components_and_fragments(self):
        url = 'http://someplace.com/resource.csv?foo=bar#foobar'
        resource_dict = {
            'url': url,
        }

        assert TabularResource.can_handle(resource_dict)

    def test_raises_valueerror_if_data_is_dict(self):
        resource_dict = {
            'data': {
                'foo': 'bar',
            },
        }

        with pytest.raises(ValueError):
            TabularResource(resource_dict).data

    def test_raises_valueerror_if_data_is_number(self):
        resource_dict = {
            'data': 51,
        }
        with pytest.raises(ValueError):
            TabularResource(resource_dict).data

    def test_raises_valueerror_if_data_is_none(self):
        resource_dict = {
            'data': None,
        }
        with pytest.raises(ValueError):
            TabularResource(resource_dict).data

    def test_raises_valueerror_if_theres_no_data(self):
        resource_dict = {}
        with pytest.raises(ValueError):
            TabularResource(resource_dict).data

    def test_iterator_with_inline_data(self):
        data = [
            {'country': 'China', 'value': '中国'},
            {'country': 'Brazil', 'value': 'Brasil'},
        ]
        resource = TabularResource({'data': data})

        assert [row for row in resource.iter()] == data

    def test_iterator_with_local_data(self, csv_tmpfile):
        csv_contents = (
            'country,value\n'
            'China,中国\n'
            'Brazil,Brasil\n'
        ).encode('utf-8')
        csv_tmpfile.write(csv_contents)
        csv_tmpfile.flush()

        resource = TabularResource({'path': csv_tmpfile.name})
        data = [row for row in resource.iter()]

        assert data == [
            {'country': 'China', 'value': '中国'},
            {'country': 'Brazil', 'value': 'Brasil'},
        ]

    def test_raises_with_wrong_encoding(self, csv_tmpfile):
        csv_contents = (
            'country,value\n'
            'China,中国\n'
            'Brazil,Brasil\n'
        ).encode('utf-8')
        csv_tmpfile.write(csv_contents)
        csv_tmpfile.flush()

        resource = TabularResource({'path': csv_tmpfile.name, 'encoding': 'utf-16'})
        with pytest.raises(ValueError):
            data = [row for row in resource.iter()]

    @httpretty.activate
    def test_iterator_with_remote_data(self):
        httpretty.HTTPretty.allow_net_connect = False
        csv_contents = (
            'country,value\n'
            'China,中国\n'
            'Brazil,Brasil\n'
        ).encode('utf-8')
        resource_dict = {
            'url': 'http://someplace.com/data.csv',
        }
        httpretty.register_uri(httpretty.GET, resource_dict['url'],
                               body=csv_contents)

        resource = TabularResource(resource_dict)

        assert [row for row in resource.iter()] == [
            {'country': 'China', 'value': '中国'},
            {'country': 'Brazil', 'value': 'Brasil'},
        ]

    def test_iterator_with_inline_non_tabular_data(self):
        resource = TabularResource({'data': 'foo'})
        with pytest.raises(ValueError):
            [row for row in resource.iter()]

    def test_iterator_with_local_non_tabular_data(self, txt_tmpfile):
        txt_tmpfile.write('foo'.encode('utf-8'))
        txt_tmpfile.flush()
        resource = TabularResource({'path': txt_tmpfile.name})
        with pytest.raises(ValueError):
            [row for row in resource.iter()]

    @httpretty.activate
    def test_iterator_with_remote_non_tabular_data(self):
        httpretty.HTTPretty.allow_net_connect = False
        resource_dict = {
            'url': 'http://someplace.com/data.txt',
        }
        httpretty.register_uri(httpretty.GET, resource_dict['url'],
                               body='foo')

        resource = TabularResource(resource_dict)

        with pytest.raises(ValueError):
            [row for row in resource.iter()]

    def test_iterator_raises_valueerror_if_theres_no_data(self):
        resource = TabularResource({})
        with pytest.raises(ValueError):
            [row for row in resource.iter()]

    def test_iterator_raises_if_file_doesnt_exist(self):
        resource = TabularResource({'path': 'inexistent-file.csv'})
        with pytest.raises(IOError):
            [row for row in resource.iter()]

    @httpretty.activate
    def test_iterator_raises_if_url_doesnt_exist(self):
        url = 'http://someplace.com/inexistent-file.csv'
        httpretty.register_uri(httpretty.GET, url, status=404)
        resource = TabularResource({'url': url})
        with pytest.raises(IOError):
            [row for row in resource.iter()]

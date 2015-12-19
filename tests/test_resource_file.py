 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import httpretty
import tests.test_helpers as test_helpers

import datapackage.exceptions
import datapackage.resource_file

InlineResourceFile = datapackage.resource_file.InlineResourceFile
LocalResourceFile = datapackage.resource_file.LocalResourceFile
RemoteResourceFile = datapackage.resource_file.RemoteResourceFile


class BasicResourceFileTests(object):
    def test_it_loads_a_file(self):
        resource_file = self._create_resource_file_with('foo.txt')
        assert resource_file.read() == b'foo\n'

    def test_read_can_be_called_multiple_times(self):
        resource_file = self._create_resource_file_with('foo.txt')

        content = resource_file.read()

        assert resource_file.read() == content

    def test_unicode(self):
        resource_file = self._create_resource_file_with('unicode.txt')

        assert resource_file.read().decode('utf-8') == '万事开头难\n'

    def test_iterator(self):
        resource_file = self._create_resource_file_with('foo.txt')
        content = [row for row in resource_file]
        assert content == [b'foo\n']

    def test_binary_data(self):
        resource_file = self._create_resource_file_with('image.gif')

        with open(test_helpers.fixture_path('image.gif'), 'rb') as f:
            assert resource_file.read() == f.read()

    def test_binary_data_iterator(self):
        resource_file = self._create_resource_file_with('image.gif')

        content = [r for r in resource_file]
        with open(test_helpers.fixture_path('image.gif'), 'rb') as f:
            assert b''.join(content) == f.read()

    def _create_resource_file_with(self, fixture):
        raise NotImplemented()


class TestInlineResourceFile(BasicResourceFileTests):
    def _create_resource_file_with(self, fixture):
        path = test_helpers.fixture_path(fixture)
        with open(path, 'rb') as f:
            return InlineResourceFile(f.read())


class TestLocalResourceFile(BasicResourceFileTests):
    def _create_resource_file_with(self, fixture):
        path = test_helpers.fixture_path(fixture)
        return LocalResourceFile(path)

    def test_it_closes_the_opened_files(self):
        resource_file = self._create_resource_file_with('foo.txt')
        the_file = resource_file._file

        assert not the_file.closed
        del resource_file
        assert the_file.closed

    def test_inexistent_path_raises_resourceerror(self):
        path = 'inexistent-file.csv'
        with pytest.raises(datapackage.exceptions.ResourceError):
            LocalResourceFile(path)


class TestRemoteResourceFile(BasicResourceFileTests):
    def setup_method(self, method):
        httpretty.enable()
        httpretty.HTTPretty.allow_net_connect = False

    def teardown_method(self, method):
        httpretty.disable()
        httpretty.reset()

    def _create_resource_file_with(self, fixture):
        path = test_helpers.fixture_path(fixture)
        with open(path, 'rb') as f:
            body = f.read()
        url = 'http://www.someplace.com/{fixture}'.format(fixture=fixture)
        httpretty.register_uri(httpretty.GET,
                               url,
                               body=body)

        return RemoteResourceFile(url)

    def test_it_closes_the_opened_files(self):
        resource_file = self._create_resource_file_with('foo.txt')
        the_file = resource_file._file

        assert not the_file.raw.closed
        del resource_file
        assert the_file.raw.closed

    def test_inexistent_url_raises_resourceerror(self):
        url = 'http://www.nowhere.com/inexistent-file.csv'
        httpretty.register_uri(httpretty.GET, url, status=404)
        with pytest.raises(datapackage.exceptions.ResourceError):
            RemoteResourceFile(url)

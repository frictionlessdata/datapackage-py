import datapackage
import posixpath
from nose.tools import raises
from mock import Mock, patch


class TestDatapackage(object):

    def setup(self):
        self.dpkg = datapackage.DataPackage("tests/test.dpkg")
        self.resource = datapackage.Resource(
            self.dpkg.uri,
            self.dpkg.descriptor['resources'][0])

    def teardown(self):
        pass

    def patch_urlopen_size(self, mock_urlopen, size):
        mock_meta = Mock()
        mock_meta.getheaders.side_effect = [[size]]

        mock_site = Mock()
        mock_site.info.return_value = mock_meta

        mock_urlopen.return_value = mock_site

    def test_get_data(self):
        """Try reading the resource data"""
        data = self.resource.data
        assert data == {"foo": "bar"}

    def test_get_missing_data(self):
        """Try reading missing resource data"""
        del self.resource.descriptor['data']
        data = self.resource.data
        assert data is None

    def test_clear_data(self):
        """Check that setting data to none removes it from the descriptor"""
        self.resource.data = None
        assert 'data' not in self.resource.descriptor

    def test_set_data(self):
        """Check that setting the data works"""
        # 1 will get converted to "1" because it gets translated into
        # a json object, and json keys are always strings
        self.resource.data = {"foo": "bar", 1: 2}
        assert self.resource.data == {"foo": "bar", "1": 2}

    def test_get_path(self):
        """Try reading the resource path"""
        path = self.resource.path
        assert path == "foobar.json"

    def test_get_fullpath(self):
        """Try reading the full resource path"""
        path = self.resource.fullpath
        assert path == posixpath.join(self.dpkg.uri, "foobar.json")
        assert posixpath.exists(path)

    def test_get_missing_path(self):
        """Try reading the path when it is missing"""
        del self.resource.descriptor['path']
        path = self.resource.path
        assert path is None

    def test_get_missing_fullpath(self):
        """Try reading the full path when it is missing"""
        del self.resource.descriptor['path']
        path = self.resource.fullpath
        assert path is None

    def test_clear_path(self):
        """Check that setting path to none removes it from the descriptor"""
        self.resource.path = None
        assert 'path' not in self.resource.descriptor

    def test_clear_fullpath(self):
        """Check that setting the full path to none removes it from the
        descriptor

        """
        self.resource.fullpath = None
        assert 'path' not in self.resource.descriptor

    def test_set_path(self):
        """Check that setting the path works"""
        self.resource.path = "barfoo.json"
        assert self.resource.path == "barfoo.json"
        assert self.resource.fullpath == posixpath.join(self.dpkg.uri, "barfoo.json")

    def test_set_fullpath(self):
        """Check that setting the full path works"""
        self.resource.fullpath = posixpath.join(self.dpkg.uri, "barfoo.json")
        assert self.resource.path == "barfoo.json"
        assert self.resource.fullpath == posixpath.join(self.dpkg.uri, "barfoo.json")

    def test_get_url(self):
        """Try reading the resource url"""
        url = self.resource.url
        assert url == "http://foobar.com/foobar.json"

    def test_get_missing_url(self):
        """Try reading the resource url when it is missing"""
        del self.resource.descriptor['url']
        url = self.resource.url
        assert url is None

    def test_clear_url(self):
        """Check that setting the url to none removes it from the descriptor"""
        self.resource.url = None
        assert 'url' not in self.resource.descriptor

    def test_set_url(self):
        """Try setting the resource url"""
        self.resource.url = "https://www.google.com"
        assert self.resource.url == "https://www.google.com"

    @raises(ValueError)
    def test_set_bad_url(self):
        """Try setting the resource url to an invalid url"""
        self.resource.url = "google"

    def test_get_name(self):
        """Try reading the resource name"""
        assert self.resource.name == "foobar"

    def test_get_default_name(self):
        """Try reading the default resource name"""
        del self.resource.descriptor['name']
        assert self.resource.name == ''

    def test_set_name(self):
        """Try setting the resource name"""
        self.resource.name = "barfoo"
        assert self.resource.name == "barfoo"

    def test_set_name_to_none(self):
        """Try setting the resource name to none"""
        self.resource.name = None
        assert self.resource.name == ''
        assert self.resource.descriptor['name'] == ''

    @raises(ValueError)
    def test_set_invalid_name(self):
        """Try setting the resource name to an invalid name"""
        self.resource.name = "foo bar"

    def test_get_format(self):
        """Try reading the resource format"""
        assert self.resource.format == "json"

    def test_get_default_format(self):
        """Try reading the default resource format"""
        del self.resource.descriptor['format']
        assert self.resource.format == ''

    def test_set_format(self):
        """Try setting the resource format"""
        self.resource.format = 'csv'
        assert self.resource.format == 'csv'

    def test_set_format_to_none(self):
        """Try setting the resource format to none"""
        self.resource.format = None
        assert self.resource.format == ''
        assert self.resource.descriptor['format'] == ''

    def test_get_mediatype(self):
        """Try reading the resource mediatype"""
        assert self.resource.mediatype == "application/json"

    def test_get_default_mediatype(self):
        """Try reading the default mediatype"""
        del self.resource.descriptor['mediatype']
        assert self.resource.mediatype == ''

    def test_set_mediatype(self):
        """Try setting the resource mediatype"""
        self.resource.mediatype = 'text/csv'
        assert self.resource.mediatype == 'text/csv'

    def test_set_mediatype_to_none(self):
        """Try setting the resource mediatype to none"""
        self.resource.mediatype = None
        assert self.resource.mediatype == ''
        assert self.resource.descriptor['mediatype'] == ''

    @raises(ValueError)
    def test_set_invalid_mediatype(self):
        """Try setting the resource mediatype to an invalid mimetype"""
        self.resource.mediatype = "foo"

    def test_get_encoding(self):
        """Try reading the resource encoding"""
        assert self.resource.encoding == 'utf-8'

    def test_get_default_encoding(self):
        """Try reading the default encoding"""
        del self.resource.descriptor['encoding']
        assert self.resource.encoding == 'utf-8'

    def test_set_encoding(self):
        """Try setting the resource encoding"""
        self.resource.encoding = 'latin1'
        assert self.resource.encoding == 'latin1'

    def test_set_encoding_to_none(self):
        """Try setting the resource encoding to none"""
        self.resource.encoding = None
        assert self.resource.encoding == 'utf-8'
        assert self.resource.descriptor['encoding'] == 'utf-8'

    def test_guess_mediatype(self):
        assert self.resource._guess_mediatype() == 'application/json'
        self.resource.path = "foo.csv"
        assert self.resource._guess_mediatype() == 'text/csv'
        self.resource.path = "foo.jpg"
        assert self.resource._guess_mediatype() == 'image/jpeg'

        self.resource.path = None
        assert self.resource._guess_mediatype() == 'application/json'
        self.resource.url = "http://foobar.com/foo.csv"
        assert self.resource._guess_mediatype() == 'text/csv'
        self.resource.url = "http://foobar.com/foo.jpg"
        assert self.resource._guess_mediatype() == 'image/jpeg'

    def test_guess_format(self):
        assert self.resource._guess_format() == 'json'
        self.resource.path = "foo.csv"
        assert self.resource._guess_format() == 'csv'
        self.resource.path = "foo.jpg"
        assert self.resource._guess_format() == 'jpg'

        self.resource.path = None
        self.resource.url = "http://foobar.com/foo.json"
        assert self.resource._guess_format() == 'json'
        self.resource.url = "http://foobar.com/foo.csv"
        assert self.resource._guess_format() == 'csv'
        self.resource.url = "http://foobar.com/foo.jpg"
        assert self.resource._guess_format() == 'jpg'

        self.resource.url = None
        self.resource.mediatype = "application/json"
        assert self.resource._guess_format() == 'json'
        self.resource.mediatype = "text/csv"
        assert self.resource._guess_format() == 'csv'
        self.resource.mediatype = "image/jpeg"
        assert self.resource._guess_format() == 'jpe'

    def test_data_bytes(self):
        """Checks that the size is computed correctly from the data"""
        assert self.resource._data_bytes() == self.resource.bytes

    @raises(ValueError)
    def test_data_bytes_no_data(self):
        """Check that an error is raised when _data_bytes is called but there
        is no data

        """
        self.resource.data = None
        self.resource._data_bytes()

    def test_path_bytes(self):
        """Checks that the size is computed correctly from the path"""
        assert self.resource._path_bytes() == self.resource.bytes

    @raises(ValueError)
    def test_path_bytes_no_path(self):
        """Check that an error is raised when _path_bytes is called but there
        is no path

        """
        self.resource.path = None
        self.resource._path_bytes()

    @patch('urllib.urlopen')
    def test_url_bytes(self, mock_urlopen):
        """Checks that the size is computed correctly from the url"""
        self.patch_urlopen_size(mock_urlopen, '14')
        assert self.resource._url_bytes() == self.resource.bytes

    @raises(ValueError)
    def test_url_bytes_no_url(self):
        """Check that an error is raised when _url_bytes is called but there
        is no url

        """
        self.resource.url = None
        self.resource._url_bytes()

    def test_compute_bytes_from_data(self):
        """Test computing the size from inline data"""
        del self.resource.descriptor['bytes']
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    def test_update_bytes_data_unchanged(self):
        """Test that updating the size from inline data does not throw an
        error when the size has not changed.

        """
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    def test_compute_bytes_from_path(self):
        """Test computing the size from the file given by the path"""
        self.resource.data = None
        del self.resource.descriptor['bytes']
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    def test_update_bytes_path_unchanged(self):
        """Test that updating the size from the file given by the path does
        not throw an error when the size has not changed.

        """
        self.resource.data = None
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    @patch('urllib.urlopen')
    def test_compute_bytes_from_url(self, mock_urlopen):
        """Test computing the size from the url"""
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.path = None
        del self.resource.descriptor['bytes']
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    @patch('urllib.urlopen')
    def test_update_bytes_url_unchanged(self, mock_urlopen):
        """Test that updating the size from the url does not throw an
        error when the size has not changed.

        """
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.path = None
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    @raises(RuntimeError)
    def test_update_bytes_data_changed(self):
        """Check that updating the bytes from the inline data throws an error
        when the size has changed.

        """
        self.resource.descriptor['bytes'] = 15
        self.resource.update_bytes()

    @raises(RuntimeError)
    def test_update_bytes_path_changed(self):
        """Check that updating the bytes from the path throws an error when
        the size has changed.

        """
        self.resource.data = None
        self.resource.descriptor['bytes'] = 15
        self.resource.update_bytes()

    @raises(RuntimeError)
    @patch('urllib.urlopen')
    def test_update_bytes_url_changed(self, mock_urlopen):
        """Check that updating the bytes from the url throws an error when the
        size has changed.

        """
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.path = None
        self.resource.descriptor['bytes'] = 15
        self.resource.update_bytes()

    def test_update_bytes_data_changed_unverified(self):
        """Check that updating the bytes from the inline data works, when the
        size has changed but the size is not being verified.

        """
        self.resource.descriptor['bytes'] = 15
        self.resource.update_bytes(verify=False)
        assert self.resource.bytes == 14
        assert self.resource.descriptor['bytes'] == 14

    def test_update_bytes_path_changed_unverified(self):
        """Check that updating the bytes from the path works, when the size
        has changed but the size is not being verified.

        """
        self.resource.data = None
        self.resource.descriptor['bytes'] = 15
        self.resource.update_bytes(verify=False)
        assert self.resource.bytes == 14
        assert self.resource.descriptor['bytes'] == 14

    @patch('urllib.urlopen')
    def test_update_bytes_url_changed_unverified(self, mock_urlopen):
        """Check that updating the bytes from the url works, when the size has
        changed but the size is not being verified.

        """
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.descriptor['bytes'] = 15
        self.resource.update_bytes(verify=False)
        assert self.resource.bytes == 14
        assert self.resource.descriptor['bytes'] == 14

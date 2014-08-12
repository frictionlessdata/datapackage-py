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

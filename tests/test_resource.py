import datapackage
from nose.tools import raises
from mock import Mock, patch


class TestDatapackage(object):

    def setup(self):
        self.dpkg = datapackage.DataPackage("tests/test.dpkg")
        self.resource = datapackage.Resource(
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

from nose.tools import raises
from datapackage import licenses as l


class TestLicenses(object):

    def setup(self):
        self.descriptor = {
            "license": "ODC-BY"
        }

    def teardown(self):
        pass

    def test_get_licenses(self):
        """Check that the licenses are successfully read"""
        licenses = l.get_licenses(self.descriptor)
        assert len(licenses) == 1
        assert licenses[0]["type"] == "ODC-BY"
        assert licenses[0]["url"] == "http://opendefinition.org/licenses/odc-by"

    def test_get_missing_licenses(self):
        """Check than an empty list is return when there are no licenses"""
        del self.descriptor['license']
        assert l.get_licenses(self.descriptor) == []

    @raises(KeyError)
    def test_get_license_and_licenses(self):
        """Check that an error is thrown when both 'license' and 'licenses'
        are defined in the datapackage, because the datapackage
        standard says that exactly one of them should be defined (not
        both).

        """
        self.descriptor['licenses'] = [
            {"type": "ODC-BY",
             "url": "http://opendefinition.org/licenses/odc-by"}]
        l.get_licenses(self.descriptor)

    def test_set_licenses(self):
        """Test setting the licenses"""
        l.set_licenses(self.descriptor, [
            {"type": "PDDL",
             "url": "http://opendefinition.org/licenses/odc-pddl"}])
        licenses = l.get_licenses(self.descriptor)
        assert len(licenses) == 1
        assert licenses[0]["type"] == "PDDL"
        assert licenses[0]["url"] == "http://opendefinition.org/licenses/odc-pddl"

    def test_add_license(self):
        """Test adding another license"""
        l.add_license(self.descriptor, "PDDL")
        licenses = l.get_licenses(self.descriptor)
        assert len(licenses) == 2
        assert licenses[0]["type"] == "ODC-BY"
        assert licenses[0]["url"] == "http://opendefinition.org/licenses/odc-by"
        assert licenses[1]["type"] == "PDDL"
        assert licenses[1]["url"] == "http://opendefinition.org/licenses/odc-pddl"

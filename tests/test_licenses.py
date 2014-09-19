from nose.tools import raises
from datapackage.licenses import License


class TestLicenses(object):

    def setup(self):
        self.license ="ODC-BY"
        self.license_url = "http://opendefinition.org/licenses/odc-by"

    def teardown(self):
        pass

    def test_add_opendefinition_licenses(self):
        """Check that the licenses are successfully read"""
        license_obj = License(type=self.license)
        assert license_obj.type == self.license
        # For Open Definition license IDs we don't need url
        assert 'url' not in license_obj

    def test_add_opendefinition_license_url(self):
        """Check to see if it's ok to add OD license as well as type"""
        license_obj = License(type=self.license, url=self.license_url)
        assert license_obj.type == self.license
        assert license_obj.url == self.license_url

    @raises(ValueError)
    def test_create_license_missing_type(self):
        License(url=self.license_url)

    @raises(AttributeError)
    def test_no_url_for_unknown_type(self):
        """Check that a url is required when the type is unknown"""
        License(type="batman")

    def test_add_ignore_case_of_type(self):
        """Check to see if not uppercase string works for license type"""
        # The Open Definition license should still be recognized even if
        # it's not uppercase. If it wouldn't, skipping the url should
        # result in an attribute error.
        license_obj = License(type=self.license.lower())
        assert license_obj.type == self.license

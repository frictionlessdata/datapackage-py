import datapackage
from nose.tools import raises
import unittest
from mock import Mock, patch


class TestDatapackage(object):

    def setup(self):
        self.dpkg = datapackage.DataPackage("tests/test.dpkg")

    def teardown(self):
        pass

    def test_get_name(self):
        """Check that the datapackage name is correctly read"""
        assert self.dpkg.name == "test.dpkg"

    def test_create_new_datapackage(self):
        """Checks if it's possible to create a new datapackage"""
        joker = datapackage.Resource(datapackage_uri='http://gotham.us/',
            name="joker", url="http://gotham.us/villains.csv")
        villains = datapackage.DataPackage(
            name="villains", license="PDDL", resources=[joker])
        assert villains.name == "villains"
        assert len(villains.resources) == 1
        assert villains.resources[0].name == "joker"

    @raises(KeyError)
    def test_get_missing_name(self):
        """Check that an error is raised when the name is missing"""
        del self.dpkg['name']
        self.dpkg.name

    @raises(KeyError)
    def test_get_empty_name(self):
        """Check that an error is raised when the name is an empty string"""
        self.dpkg['name'] = ""
        self.dpkg.name

    @raises(KeyError)
    def test_get_name_when_none(self):
        """Check that an error is raised when the name is None"""
        self.dpkg['name'] = None
        self.dpkg.name

    def test_set_name(self):
        """Check that the name is correctly set"""
        self.dpkg.name = "foo"
        assert self.dpkg.name == "foo"

    @raises(ValueError)
    def test_set_empty_name(self):
        """Check that an error is thrown when name is set to an empty
        string"""
        self.dpkg.name = ""

    @raises(ValueError)
    def test_set_name_as_none(self):
        """Check than an error is thrown when name is set to None"""
        self.dpkg.name = None

    def test_get_datapackage_version(self):
        """Test getting the datapackage version"""
        assert self.dpkg.datapackage_version == "1.0-beta.10"
 
    @raises(ValueError)
    def test_get_empty_datapackage_version(self):
        """Check that an error is thrown then the datapackage version is an
        empty string
        """
        self.dpkg.datapackage_version = ""

    @raises(ValueError)
    def test_get_datapackage_version_when_none(self):
        """Check that an error is thrown when the datapackage version is
        None
        """
        self.dpkg.datapackage_version = None

    def test_get_title(self):
        """Check that the title is successfully read"""
        assert self.dpkg.title == "A simple datapackage for testing"

    def test_remove_title(self):
        """Check that the title is removed"""
        del self.dpkg['title']
        assert 'title' not in self.dpkg

    def test_set_title(self):
        """Test setting the title to various values"""
        self.dpkg.title = "foo"
        assert self.dpkg.title == "foo"
        self.dpkg.title = None
        assert 'title' not in self.dpkg

    def test_get_description(self):
        """Test reading the description"""
        assert self.dpkg.description == "A simple, bare datapackage created for testing purposes."

    def test_remove_description(self):
        """Check that the description is removed"""
        del self.dpkg['description']
        assert 'description' not in self.dpkg

    def test_set_description(self):
        """Test setting the description to various values"""
        self.dpkg.description = "foo"
        assert self.dpkg.description == "foo"
        self.dpkg.description = None
        assert 'description' not in self.dpkg

    def test_get_homepage(self):
        """Test reading the homepage"""
        assert self.dpkg.homepage == "http://localhost/"

    def test_remove_homepage(self):
        """Check that the homepage is removed"""
        del self.dpkg['homepage']
        assert 'homepage' not in self.dpkg

    def test_set_homepage(self):
        """Test setting the homepage to various values"""
        self.dpkg.homepage = "http://foo.com/"
        assert self.dpkg.homepage == "http://foo.com/"
        self.dpkg.homepage = None
        assert 'homepage' not in self.dpkg

    @raises(ValueError)
    def test_set_invalid_homepage(self):
        """Test setting the homepage to an invalid URL"""
        self.dpkg.homepage = "foo"

    def test_get_version(self):
        """Test reading the version"""
        assert self.dpkg.version == "1.0.0"

    def test_get_default_version(self):
        """Check that the default version is correct"""
        del self.dpkg['version']
        assert self.dpkg.version == "0.0.1"

    def test_set_version(self):
        """Test that setting the version works"""
        self.dpkg.version = "2.0.0"
        assert self.dpkg.version == "2.0.0"

    @raises(ValueError, AttributeError)
    def test_set_bad_version(self):
        """Try setting the version to one that does not follow semantic
        versioning

        """
        self.dpkg.version = "foo"

    def test_get_keywords(self):
        """Try reading the keywords"""
        assert self.dpkg.keywords == ["testing"]

    def test_remove_keywords(self):
        """Check that the keywords are removed"""
        del self.dpkg['keywords']
        assert 'keywords' not in self.dpkg

    def test_set_keywords(self):
        """Try setting keywords to something else"""
        self.dpkg.keywords = ["foo", "bar"]
        assert self.dpkg.keywords == ["foo", "bar"]

    def test_get_image(self):
        """Try reading the image name"""
        assert self.dpkg.image == "test.jpg"

    def test_remove_image(self):
        """Check that the image is removed"""
        del self.dpkg['image']
        assert 'image' not in self.dpkg

    def test_set_image(self):
        """Try setting the image to other values"""
        self.dpkg.image = None
        assert 'image' not in self.dpkg
        self.dpkg.image = "bar.jpg"
        assert self.dpkg.image == "bar.jpg"

    @patch('urllib.urlopen')
    def test_web_url(self, mock_urlopen):
        """Try reading a datapackage from the web"""

        # setup the mock for url read
        with open("tests/cpi/datapackage.json", "r") as fh:
            metadata = fh.read()
        mock = Mock()
        mock.read.side_effect = [metadata]
        mock_urlopen.return_value = mock

        self.dpkg = datapackage.DataPackage('http://data.okfn.org/data/cpi/')
        assert self.dpkg.title == "Annual Consumer Price Index (CPI)"
        assert self.dpkg.description == "Annual Consumer Price Index (CPI) for most countries in the world. Reference year is 2005."

    def test_bump_major_version(self):
        """Tests bumping the major version of the datapackage"""
        self.dpkg.version = "1.0.0"
        self.dpkg.bump_major_version()
        assert self.dpkg.version == "2.0.0"

        self.dpkg.version = "1.1.0"
        self.dpkg.bump_major_version()
        assert self.dpkg.version == "2.0.0"

        self.dpkg.version = "1.0.1"
        self.dpkg.bump_major_version()
        assert self.dpkg.version == "2.0.0"

        self.dpkg.version = "1.0.1-foo"
        self.dpkg.bump_major_version()
        assert self.dpkg.version == "2.0.0"

        self.dpkg.version = "1.0.1-foo+bar"
        self.dpkg.bump_major_version()
        assert self.dpkg.version == "2.0.0"

        self.dpkg.version = "1.0.1-foo+bar"
        self.dpkg.bump_major_version(True)
        assert self.dpkg.version == "2.0.0+bar"

    def test_bump_minor_version(self):
        """Tests bumping the minor version of the datapackage"""
        self.dpkg.version = "1.0.0"
        self.dpkg.bump_minor_version()
        assert self.dpkg.version == "1.1.0"

        self.dpkg.version = "1.1.0"
        self.dpkg.bump_minor_version()
        assert self.dpkg.version == "1.2.0"

        self.dpkg.version = "1.0.1"
        self.dpkg.bump_minor_version()
        assert self.dpkg.version == "1.1.0"

        self.dpkg.version = "1.0.1-foo"
        self.dpkg.bump_minor_version()
        assert self.dpkg.version == "1.1.0"

        self.dpkg.version = "1.0.1-foo+bar"
        self.dpkg.bump_minor_version()
        assert self.dpkg.version == "1.1.0"

        self.dpkg.version = "1.0.1-foo+bar"
        self.dpkg.bump_minor_version(True)
        assert self.dpkg.version == "1.1.0+bar"

    def test_bump_patch_version(self):
        """Tests bumping the patch version of the datapackage"""
        self.dpkg.version = "1.0.0"
        self.dpkg.bump_patch_version()
        assert self.dpkg.version == "1.0.1"

        self.dpkg.version = "1.1.0"
        self.dpkg.bump_patch_version()
        assert self.dpkg.version == "1.1.1"

        self.dpkg.version = "1.0.1"
        self.dpkg.bump_patch_version()
        assert self.dpkg.version == "1.0.2"

        self.dpkg.version = "1.0.1-foo"
        self.dpkg.bump_patch_version()
        assert self.dpkg.version == "1.0.2"

        self.dpkg.version = "1.0.1-foo+bar"
        self.dpkg.bump_patch_version()
        assert self.dpkg.version == "1.0.2"

        self.dpkg.version = "1.0.1-foo+bar"
        self.dpkg.bump_patch_version(True)
        assert self.dpkg.version == "1.0.2+bar"

    def test_get_license_and_licenses(self):
        """Check that when setting licenses in a data package with
        a license the license value is removed because the datapackage
        standard says that exactly one of them should be defined (not
        both).

        """
        assert 'license' in self.dpkg
        assert 'licenses' not in self.dpkg
        self.dpkg.licenses = [
            {"type": "ODC-BY",
             "url": "http://opendefinition.org/licenses/odc-by"}]
        assert 'license' not in self.dpkg
        assert 'licenses' in self.dpkg

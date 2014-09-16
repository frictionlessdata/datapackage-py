import datapackage
from nose.tools import raises
from mock import Mock, patch


class TestDatapackage(object):

    def setup(self):
        self.dpkg = datapackage.DataPackage("tests/test.dpkg")

    def teardown(self):
        pass

    def test_get_name(self):
        """Check that the datapackage name is correctly read"""
        assert self.dpkg.name == "test.dpkg"

    @raises(KeyError)
    def test_get_missing_name(self):
        """Check that an error is raised when the name is missing"""
        del self.dpkg.descriptor['name']
        self.dpkg.name

    @raises(KeyError)
    def test_get_empty_name(self):
        """Check that an error is raised when the name is an empty string"""
        self.dpkg.descriptor['name'] = ""
        self.dpkg.name

    @raises(KeyError)
    def test_get_name_when_none(self):
        """Check that an error is raised when the name is None"""
        self.dpkg.descriptor['name'] = None
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

    @raises(KeyError)
    def test_get_missing_datapackage_version(self):
        """Check than an error is thrown when the datapackage version is
        missing

        """
        del self.dpkg.descriptor['datapackage_version']
        self.dpkg.datapackage_version

    @raises(KeyError)
    def test_get_empty_datapackage_version(self):
        """Check that an error is thrown then the datapackage version is an
        empty string

        """
        self.dpkg.descriptor['datapackage_version'] = ""
        self.dpkg.datapackage_version

    @raises(KeyError)
    def test_get_datapackage_version_when_none(self):
        """Check that an error is thrown when the datapackage version is
        None

        """
        self.dpkg.descriptor['datapackage_version'] = None
        self.dpkg.datapackage_version

    def test_get_title(self):
        """Check that the title is successfully read"""
        assert self.dpkg.title == "A simple datapackage for testing"

    def test_get_default_title(self):
        """Check that the default title is correct"""
        del self.dpkg.descriptor['title']
        assert self.dpkg.title == ""

    def test_set_title(self):
        """Test setting the title to various values"""
        self.dpkg.title = "foo"
        assert self.dpkg.title == "foo"
        self.dpkg.title = None
        assert self.dpkg.title == ""

    def test_get_description(self):
        """Test reading the description"""
        assert self.dpkg.description == "A simple, bare datapackage created for testing purposes."

    def test_get_default_description(self):
        """Check that the default description is correct"""
        del self.dpkg.descriptor['description']
        assert self.dpkg.description == ""

    def test_set_description(self):
        """Test setting the description to various values"""
        self.dpkg.description = "foo"
        assert self.dpkg.description == "foo"
        self.dpkg.description = None
        assert self.dpkg.description == ""

    def test_get_homepage(self):
        """Test reading the homepage"""
        assert self.dpkg.homepage == "http://localhost/"

    def test_get_default_homepage(self):
        """Check that the default homepage is correct"""
        del self.dpkg.descriptor['homepage']
        assert self.dpkg.homepage == ""

    def test_set_homepage(self):
        """Test setting the homepage to various values"""
        self.dpkg.homepage = "http://foo.com/"
        assert self.dpkg.homepage == "http://foo.com/"
        self.dpkg.homepage = None
        assert self.dpkg.homepage == ""

    @raises(ValueError)
    def test_set_invalid_homepage(self):
        """Test setting the homepage to an invalid URL"""
        self.dpkg.homepage = "foo"

    def test_get_version(self):
        """Test reading the version"""
        assert self.dpkg.version == "1.0.0"

    def test_get_default_version(self):
        """Check that the default version is correct"""
        del self.dpkg.descriptor['version']
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

    def test_get_default_keywords(self):
        """Check that the default keywords are correct"""
        del self.dpkg.descriptor['keywords']
        assert self.dpkg.keywords == []

    def test_set_keywords(self):
        """Try setting keywords to something else"""
        self.dpkg.keywords = ["foo", "bar"]
        assert self.dpkg.keywords == ["foo", "bar"]

    def test_get_image(self):
        """Try reading the image name"""
        assert self.dpkg.image == "test.jpg"

    def test_get_default_image(self):
        """Check that the default image is correct"""
        del self.dpkg.descriptor['image']
        assert self.dpkg.image == ''

    def test_set_image(self):
        """Try setting the image to other values"""
        self.dpkg.image = None
        assert self.dpkg.image == ''
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

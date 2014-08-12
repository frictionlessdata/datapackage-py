from datapackage import DataPackage
from nose.tools import raises


class TestDatapackage(object):

    def setup(self):
        self.dpkg = DataPackage("tests/test.dpkg")

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

    def test_get_licenses(self):
        """Check that the licenses are successfully read"""
        licenses = self.dpkg.licenses
        assert len(licenses) == 1
        assert licenses[0]["type"] == "ODC-BY"
        assert licenses[0]["url"] == "http://opendefinition.org/licenses/odc-by"

    @raises(KeyError)
    def test_get_missing_licenses(self):
        """Check than an error is thrown when there are no licenses"""
        del self.dpkg.descriptor['license']
        self.dpkg.licenses

    @raises(KeyError)
    def test_get_license_and_licenses(self):
        """Check that an error is thrown when both 'license' and 'licenses'
        are defined in the datapackage, because the datapackage
        standard says that exactly one of them should be defined (not
        both).

        """
        self.dpkg.descriptor['licenses'] = [
            {"type": "ODC-BY",
             "url": "http://opendefinition.org/licenses/odc-by"}]
        self.dpkg.licenses

    def test_set_licenses(self):
        """Test setting the licenses"""
        self.dpkg.licenses = [
            {"type": "PDDL",
             "url": "http://opendefinition.org/licenses/odc-pddl"}]
        assert len(self.dpkg.licenses) == 1
        assert self.dpkg.licenses[0]["type"] == "PDDL"
        assert self.dpkg.licenses[0]["url"] == "http://opendefinition.org/licenses/odc-pddl"

    def test_add_license(self):
        """Test adding another license"""
        self.dpkg.add_license("PDDL")
        assert len(self.dpkg.licenses) == 2
        assert self.dpkg.licenses[0]["type"] == "ODC-BY"
        assert self.dpkg.licenses[0]["url"] == "http://opendefinition.org/licenses/odc-by"
        assert self.dpkg.licenses[1]["type"] == "PDDL"
        assert self.dpkg.licenses[1]["url"] == "http://opendefinition.org/licenses/odc-pddl"

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

    def test_get_sources(self):
        """Try reading the sources"""
        assert len(self.dpkg.sources) == 1
        assert self.dpkg.sources[0]["name"] == "World Bank and OECD"
        assert self.dpkg.sources[0]["web"] == "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"

    def test_get_default_sources(self):
        """Check that the default sources are correct"""
        del self.dpkg.descriptor['sources']
        assert self.dpkg.sources == []

    def test_set_sources(self):
        """Check that setting the sources works"""
        self.dpkg.sources = None
        assert len(self.dpkg.sources) == 0
        self.dpkg.sources = [{"name": "foo", "web": "https://bar.com/"}]
        assert len(self.dpkg.sources) == 1
        assert self.dpkg.sources[0]["name"] == "foo"
        assert self.dpkg.sources[0]["web"] == "https://bar.com/"

    @raises(ValueError)
    def test_set_sources_bad_keys(self):
        """Check that an error occurs when the source keys are invalid"""
        self.dpkg.sources = [{"foo": "foo", "bar": "bar"}]

    @raises(ValueError)
    def test_set_sources_missing_name(self):
        """Check that an error occurs when the source name is missing"""
        self.dpkg.sources = [{"web": "foo", "email": "bar"}]

    @raises(ValueError)
    def test_set_sources_duplicate_names(self):
        """Check that an error occurs when there are duplicate sources"""
        self.dpkg.sources = [
            {"name": "foo", "email": "bar"},
            {"name": "foo", "email": "baz"}]

    @raises(ValueError)
    def test_set_sources_bad_website(self):
        """Check that an error occurs when the web URL is invalid"""
        self.dpkg.sources = [{"name": "foo", "email": "bar"}]

    @raises(ValueError)
    def test_set_sources_bad_email(self):
        """Check that an error occurs when the email is invalid"""
        self.dpkg.sources = [{"name": "foo", "web": "bar"}]

    def test_add_source(self):
        """Try adding a new source with add_source"""
        self.dpkg.add_source("foo", email="bar@test.com")
        assert len(self.dpkg.sources) == 2
        assert self.dpkg.sources[0]["name"] == "World Bank and OECD"
        assert self.dpkg.sources[0]["web"] == "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
        assert self.dpkg.sources[1]["name"] == "foo"
        assert self.dpkg.sources[1]["email"] == "bar@test.com"

    def test_remove_source(self):
        """Try removing a source with remove_source"""
        self.dpkg.remove_source("World Bank and OECD")
        assert len(self.dpkg.sources) == 0

    @raises(KeyError)
    def test_remove_bad_source(self):
        """Check that an error occurs when removing a non-existant source"""
        self.dpkg.remove_source("foo")

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

    def test_web_url(self):
        """Try reading a datapackage from the web"""
        self.dpkg = DataPackage('http://data.okfn.org/data/cpi/')
        assert self.dpkg.title == "Annual Consumer Price Index (CPI)"
        assert self.dpkg.description == "Annual Consumer Price Index (CPI) for most countries in the world. Reference year is 2005."

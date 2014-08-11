from datapackage import DataPackage
from nose.tools import raises


def test_get_name():
    """Check that the datapackage name is correctly read"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.name == "test.dpkg"


@raises(KeyError)
def test_get_missing_name():
    """Check that an error is raised when the name is missing"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['name']
    dpkg.name


@raises(KeyError)
def test_get_empty_name():
    """Check that an error is raised when the name is an empty string"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.descriptor['name'] = ""
    dpkg.name


@raises(KeyError)
def test_get_name_when_none():
    """Check that an error is raised when the name is None"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.descriptor['name'] = None
    dpkg.name


def test_set_name():
    """Check that the name is correctly set"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.name = "foo"
    assert dpkg.name == "foo"


@raises(ValueError)
def test_set_empty_name():
    """Check that an error is thrown when name is set to an empty string"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.name = ""


@raises(ValueError)
def test_set_name_as_none():
    """Check than an error is thrown when name is set to None"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.name = None


def test_get_licenses():
    """Check that the licenses are successfully read"""
    dpkg = DataPackage("tests/test.dpkg")
    licenses = dpkg.licenses
    assert len(licenses) == 1
    assert licenses[0]["type"] == "ODC-BY"
    assert licenses[0]["url"] == "http://opendefinition.org/licenses/odc-by"


@raises(KeyError)
def test_get_missing_licenses():
    """Check than an error is thrown when there are no licenses"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['license']
    dpkg.licenses


@raises(KeyError)
def test_get_license_and_licenses():
    """Check that an error is thrown when both 'license' and 'licenses'
    are defined in the datapackage, because the datapackage standard
    says that exactly one of them should be defined (not both).

    """
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.descriptor['licenses'] = [
        {"type": "ODC-BY", "url": "http://opendefinition.org/licenses/odc-by"}]
    dpkg.licenses


def test_set_licenses():
    """Test setting the licenses"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.licenses = [
        {"type": "PDDL", "url": "http://opendefinition.org/licenses/odc-pddl"}]
    assert len(dpkg.licenses) == 1
    assert dpkg.licenses[0]["type"] == "PDDL"
    assert dpkg.licenses[0]["url"] == "http://opendefinition.org/licenses/odc-pddl"


def test_add_license():
    """Test adding another license"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.add_license("PDDL")
    assert len(dpkg.licenses) == 2
    assert dpkg.licenses[0]["type"] == "ODC-BY"
    assert dpkg.licenses[0]["url"] == "http://opendefinition.org/licenses/odc-by"
    assert dpkg.licenses[1]["type"] == "PDDL"
    assert dpkg.licenses[1]["url"] == "http://opendefinition.org/licenses/odc-pddl"


def test_get_datapackage_version():
    """Test getting the datapackage version"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.datapackage_version == "1.0-beta.10"


@raises(KeyError)
def test_get_missing_datapackage_version():
    """Check than an error is thrown when the datapackage version is missing"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['datapackage_version']
    dpkg.datapackage_version


@raises(KeyError)
def test_get_empty_datapackage_version():
    """Check that an error is thrown then the datapackage version is an
    empty string"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.descriptor['datapackage_version'] = ""
    dpkg.datapackage_version


@raises(KeyError)
def test_get_datapackage_version_when_none():
    """Check that an error is thrown when the datapackage version is None"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.descriptor['datapackage_version'] = None
    dpkg.datapackage_version


def test_get_title():
    """Check that the title is successfully read"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.title == "A simple datapackage for testing"


def test_get_default_title():
    """Check that the default title is correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['title']
    assert dpkg.title == ""


def test_set_title():
    """Test setting the title to various values"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.title = "foo"
    assert dpkg.title == "foo"
    dpkg.title = None
    assert dpkg.title == ""


def test_get_description():
    """Test reading the description"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.description == "A simple, bare datapackage created for testing purposes."


def test_get_default_description():
    """Check that the default description is correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['description']
    assert dpkg.description == ""


def test_set_description():
    """Test setting the description to various values"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.description = "foo"
    assert dpkg.description == "foo"
    dpkg.description = None
    assert dpkg.description == ""


def test_get_homepage():
    """Test reading the homepage"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.homepage == "http://localhost/"


def test_get_default_homepage():
    """Check that the default homepage is correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['homepage']
    assert dpkg.homepage == ""


def test_set_homepage():
    """Test setting the homepage to various values"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.homepage = "foo"
    assert dpkg.homepage == "foo"
    dpkg.homepage = None
    assert dpkg.homepage == ""


def test_get_version():
    """Test reading the version"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.version == "1.0.0"


def test_get_default_version():
    """Check that the default version is correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['version']
    assert dpkg.version == "0.0.1"


def test_set_version():
    """Test that setting the version works"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.version = "2.0.0"
    assert dpkg.version == "2.0.0"


@raises(ValueError, AttributeError)
def test_set_bad_version():
    """Try setting the version to one that does not follow semantic
    versioning"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.version = "foo"


def test_get_sources():
    """Try reading the sources"""
    dpkg = DataPackage("tests/test.dpkg")
    assert len(dpkg.sources) == 1
    assert dpkg.sources[0]["name"] == "World Bank and OECD"
    assert dpkg.sources[0]["web"] == "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"


def test_get_default_sources():
    """Check that the default sources are correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['sources']
    assert dpkg.sources == []


def test_set_sources():
    """Check that setting the sources works"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.sources = None
    assert len(dpkg.sources) == 0
    dpkg.sources = [{"name": "foo", "web": "bar"}]
    assert len(dpkg.sources) == 1
    assert dpkg.sources[0]["name"] == "foo"
    assert dpkg.sources[0]["web"] == "bar"


@raises(ValueError)
def test_set_sources_bad_keys():
    """Check that an error occurs when the source keys are invalid"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.sources = [{"foo": "foo", "bar": "bar"}]


@raises(ValueError)
def test_set_sources_missing_name():
    """Check that an error occurs when the source name is missing"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.sources = [{"web": "foo", "email": "bar"}]


@raises(ValueError)
def test_set_sources_duplicate_names():
    """Check that an error occurs when there are duplicate sources"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.sources = [{"name": "foo", "email": "bar"},
                    {"name": "foo", "email": "baz"}]


def test_add_source():
    """Try adding a new source with add_source"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.add_source("foo", email="bar")
    assert len(dpkg.sources) == 2
    assert dpkg.sources[0]["name"] == "World Bank and OECD"
    assert dpkg.sources[0]["web"] == "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
    assert dpkg.sources[1]["name"] == "foo"
    assert dpkg.sources[1]["email"] == "bar"


def test_remove_source():
    """Try removing a source with remove_source"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.remove_source("World Bank and OECD")
    assert len(dpkg.sources) == 0


@raises(KeyError)
def test_remove_bad_source():
    """Check that an error occurs when removing a non-existant source"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.remove_source("foo")


def test_get_keywords():
    """Try reading the keywords"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.keywords == ["testing"]


def test_get_default_keywords():
    """Check that the default keywords are correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['keywords']
    assert dpkg.keywords == []


def test_set_keywords():
    """Try setting keywords to something else"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.keywords = ["foo", "bar"]
    assert dpkg.keywords == ["foo", "bar"]


def test_get_image():
    """Try reading the image name"""
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.image == "test.jpg"


def test_get_default_image():
    """Check that the default image is correct"""
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['image']
    assert dpkg.image == ''


def test_set_image():
    """Try setting the image to other values"""
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.image = None
    assert dpkg.image == ''
    dpkg.image = "bar.jpg"
    assert dpkg.image == "bar.jpg"


def test_web_url():
    """Try reading a datapackage from the web"""
    dpkg = DataPackage('http://data.okfn.org/data/cpi/')
    assert dpkg.title == "Annual Consumer Price Index (CPI)"
    assert dpkg.description == "Annual Consumer Price Index (CPI) for most countries in the world. Reference year is 2005."

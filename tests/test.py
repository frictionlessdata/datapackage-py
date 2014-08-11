from datapackage import DataPackage
from nose.tools import raises


def test_get_name():
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.name == "test.dpkg"


@raises(KeyError)
def test_missing_name():
    dpkg = DataPackage("tests/test.dpkg")
    del dpkg.descriptor['name']
    dpkg.name


def test_set_name():
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.name = "foo"
    assert dpkg.name == "foo"


@raises(ValueError)
def test_set_empty_name():
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.name = ""


@raises(ValueError)
def test_set_empty_name2():
    dpkg = DataPackage("tests/test.dpkg")
    dpkg.name = None


def test_get_datapackage_version():
    dpkg = DataPackage("tests/test.dpkg")
    assert dpkg.datapackage_version == "1.0-beta.10"

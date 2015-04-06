# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datapackage.util as util
from nose.tools import raises


def test_parse_version():
    """Try parsing a variety of different version strings"""
    assert util.parse_version("1.0.0") == (1, 0, 0, None, None)
    assert util.parse_version("1.0.0-alpha") == (1, 0, 0, "alpha", None)
    assert util.parse_version("1.0.0-alpha.1") == (1, 0, 0, "alpha.1", None)
    assert util.parse_version("1.0.0-0.3.7") == (1, 0, 0, "0.3.7", None)
    assert util.parse_version("1.0.0-x.7.z.92") == (1, 0, 0, "x.7.z.92", None)
    assert util.parse_version("1.0.0-alpha+001") == (1, 0, 0, "alpha", "001")
    assert util.parse_version("1.0.0+20130313144700") == (1, 0, 0, None, "20130313144700")
    assert util.parse_version("1.0.0-beta+exp.sha.5114f85") == (1, 0, 0, "beta", "exp.sha.5114f85")


@raises(ValueError)
def test_parse_version_invalid_major():
    """Check that an error is raised when the major version is invalid"""
    util.parse_version("1-alpha.0.0")


@raises(ValueError)
def test_parse_version_invalid_minor():
    """Check that an error is raised when the minor version is invalid"""
    util.parse_version("1.0-alpha.0")


@raises(ValueError)
def test_parse_version_invalid_patch():
    """Check that an error is raised when the patch version is invalid"""
    util.parse_version("1.0.0~alpha")


@raises(ValueError)
def test_parse_version_invalid_prerelease():
    """Check that an error is raised when the prerelease version is invalid"""
    util.parse_version("1.0.0-alpha~1")


@raises(ValueError)
def test_parse_version_invalid_metadata():
    """Check that an error is raised when the metadata is invalid"""
    util.parse_version("1.0.0-alpha+foo~bar")


def test_format_version():
    """Check that version tuples are formatted to the correct strings"""
    assert "1.0.0" == util.format_version((1, 0, 0, None, None))
    assert "1.0.0-alpha" == util.format_version((1, 0, 0, "alpha", None))
    assert "1.0.0-alpha.1" == util.format_version((1, 0, 0, "alpha.1", None))
    assert "1.0.0-0.3.7" == util.format_version((1, 0, 0, "0.3.7", None))
    assert "1.0.0-x.7.z.92" == util.format_version((1, 0, 0, "x.7.z.92", None))
    assert "1.0.0-alpha+001" == util.format_version((1, 0, 0, "alpha", "001"))
    assert "1.0.0+20130313144700" == util.format_version((1, 0, 0, None, "20130313144700"))
    assert "1.0.0-beta+exp.sha.5114f85" == util.format_version((1, 0, 0, "beta", "exp.sha.5114f85"))


def test_verify_version():
    """Check that version strings are correctly parsed and formatted"""
    versions = ["1.0.0", "1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-0.3.7",
                "1.0.0-x.7.z.92", "1.0.0-alpha+001", "1.0.0+20130313144700",
                "1.0.0-beta+exp.sha.5114f85"]

    for version in versions:
        assert util.verify_version(version) == version

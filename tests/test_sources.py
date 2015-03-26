# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from nose.tools import raises
from datapackage.sources import Source
from datapackage import compat


class TestSources(object):

    def setup(self):
        self.name = str("World Bank and OECD")
        self.web = str("http://data.worldbank.org/indicator/NY.GDP.MKTP.CD")
        self.email = str("info@worldbank.org")

    def teardown(self):
        pass

    def test_create_source(self):
        """Try creating a new Source object"""
        source_obj = Source(name=self.name, web=self.web, email=self.email)
        assert source_obj.name == self.name
        assert source_obj.web == self.web
        assert source_obj.email == self.email

    @raises(AttributeError)
    def test_set_sources_bad_keys(self):
        """Check that an error occurs when the source keys are invalid"""
        Source(foo="foo", bar="bar")

    @raises(ValueError)
    def test_set_sources_bad_website(self):
        """Check that an error occurs when the web URL is invalid"""
        Source(name="foo", web="bar")

    @raises(ValueError)
    def test_set_sources_bad_email(self):
        """Check that an error occurs when the email is invalid"""
        Source(name="foo", email="bar")

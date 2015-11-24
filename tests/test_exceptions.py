from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import datapackage_validate.exceptions as exceptions


class TestExceptions(unittest.TestCase):
    def test_errors_should_be_an_empty_list_by_default(self):
        exception = exceptions.DataPackageValidateException()
        assert exception.errors == []

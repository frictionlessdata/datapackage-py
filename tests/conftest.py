 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
import tempfile
from datapackage import DataPackage


# Fixtures

@pytest.yield_fixture()
def tmpfile():
    with tempfile.NamedTemporaryFile() as file:
        yield file


@pytest.yield_fixture()
def txt_tmpfile():
    with tempfile.NamedTemporaryFile(suffix='.txt') as file:
        yield file


@pytest.yield_fixture()
def csv_tmpfile():
    with tempfile.NamedTemporaryFile(suffix='.csv') as file:
        yield file


@pytest.yield_fixture()
def json_tmpfile():
    with tempfile.NamedTemporaryFile(suffix='.json') as file:
        yield file

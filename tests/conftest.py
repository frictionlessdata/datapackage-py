 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import tempfile


@pytest.yield_fixture()
def tmpfile():
    with tempfile.NamedTemporaryFile() as f:
        yield f


@pytest.yield_fixture()
def txt_tmpfile():
    with tempfile.NamedTemporaryFile(suffix='.txt') as f:
        yield f


@pytest.yield_fixture()
def csv_tmpfile():
    with tempfile.NamedTemporaryFile(suffix='.csv') as f:
        yield f

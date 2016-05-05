# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
try:
    import mock
except ImportError:
    import unittest.mock as mock

from tests import test_helpers
from datapackage import cli


class CommandCaller(object):

    def __init__(self, args):
        stdout = six.BytesIO()
        stderr = six.BytesIO()
        with mock.patch('sys.exit') as exit_mock:
            cli.main(args, stdout, stderr)
            if exit_mock.call_args:
                self.exit_code = exit_mock.call_args[0][0]
            else:
                self.exit_code = None
        self.stdout = stdout.getvalue().decode('utf-8')
        self.stderr = stderr.getvalue().decode('utf-8')


def test_validate():
    path = test_helpers.fixture_path('datapackage/datapackage.json')
    result = CommandCaller(['validate', path])
    assert result.exit_code == 0
    assert result.stdout == 'valid\n'


def test_validate_dir():
    path = test_helpers.fixture_path('datapackage')
    result = CommandCaller(['validate', path])
    assert result.exit_code == 0
    assert result.stdout == 'valid\n'


def test_validate_schema_error():
    path = test_helpers.fixture_path('empty_datapackage.json')
    result = CommandCaller(['validate', path])
    assert result.exit_code == 1
    if six.PY2:
        assert result.stderr.startswith("Error: u'name' is a required property\n")
    else:
        assert result.stderr.startswith("Error: 'name' is a required property\n")


def test_validate_file_error():
    path = test_helpers.fixture_path('missing_datapackage.json')
    result = CommandCaller(['validate', path])
    assert result.exit_code == 1
    assert result.stderr == (
        "Error: '%s' is neither an existing directory neither an existing "
        "file.\n"
    ) % path

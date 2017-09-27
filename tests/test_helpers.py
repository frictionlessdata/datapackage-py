 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile
import pytest
import datapackage.helpers as helpers


# Tests

def test_ensure_dir():
    base_path = tempfile.mkdtemp()
    try:
        dir_path = os.path.join(base_path, 'dir')
        file_path = os.path.join(dir_path, 'file')
        assert not os.path.isdir(dir_path)
        helpers.ensure_dir(file_path)
        assert os.path.isdir(dir_path)
    finally:
        shutil.rmtree(base_path)


@pytest.mark.parametrize('path,is_safe', (
    ('data.csv', True),
    ('data/data.csv', True),
    ('data/country/data.csv', True),
    ('data\\data.csv', True),
    ('data\\country\\data.csv', True),

    ('../data.csv', False),
    ('~/data.csv', False),
    ('~invalid_user/data.csv', False),
    ('%userprofile%', False),
    ('%unknown_windows_var%', False),
    ('$HOME', False),
    ('$UNKNOWN_VAR', False),
))
def test_is_safe_path(path, is_safe):
    assert helpers.is_safe_path(path) is is_safe

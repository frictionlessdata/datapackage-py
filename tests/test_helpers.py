 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil
import tempfile
from datapackage.helpers import ensure_dir


# Tests

def test_ensure_dir():
    base_path = tempfile.mkdtemp()
    try:
        dir_path = os.path.join(base_path, 'dir')
        file_path = os.path.join(dir_path, 'file')
        assert not os.path.isdir(dir_path)
        ensure_dir(file_path)
        assert os.path.isdir(dir_path)
    finally:
        shutil.rmtree(base_path)

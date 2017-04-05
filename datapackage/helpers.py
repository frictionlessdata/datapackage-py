# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os


# Module API

def ensure_dir(path):
    """Ensure directory exists.
    """
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)


def is_safe_path(path):
    """Check if path is safe and allowed.
    """
    if os.path.isabs(path):
        return Fale
    if '..%s' % os.path.sep in path:
        return False
    return True

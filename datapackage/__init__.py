# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# Module API

from .package import Package
from .resource import Resource
from .profile import Profile
from .validate import validate
from .infer import infer


# Version

import io
import os
__version__ = io.open(
    os.path.join(os.path.dirname(__file__), 'VERSION'),
    encoding='utf-8').read().strip()


# Deprecated

from .pushpull import push_datapackage, pull_datapackage
DataPackage = Package

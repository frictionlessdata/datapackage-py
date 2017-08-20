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


# Deprecated

from .pushpull import push_datapackage, pull_datapackage
DataPackage = Package

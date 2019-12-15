# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from . import config
__version__ = config.VERSION


# Module API

from .cli import cli
from .package import Package
from .resource import Resource
from .group import Group
from .profile import Profile
from .validate import validate
from .infer import infer


# Deprecated

from .pushpull import push_datapackage, pull_datapackage
DataPackage = Package

# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import json
import pytest
import requests


# Tests

def test_profiles_registry_is_up_to_date():
    local = io.open('datapackage/profiles/registry.json').read()
    remote = requests.get('https://specs.frictionlessdata.io/schemas/registry.json').text
    assert local == remote, 'run `make profiles` to update profiles'


def test_profiles_data_package_is_up_to_date():
    local = io.open('datapackage/profiles/data-package.json').read()
    remote = requests.get('https://specs.frictionlessdata.io/schemas/data-package.json').text
    assert local == remote, 'run `make profiles` to update profiles'


def test_profiles_tabular_data_package_is_up_to_date():
    local = io.open('datapackage/profiles/tabular-data-package.json').read()
    remote = requests.get('https://specs.frictionlessdata.io/schemas/tabular-data-package.json').text
    assert local == remote, 'run `make profiles` to update profiles'


def test_profiles_fiscal_data_package_is_up_to_date():
    local = io.open('datapackage/profiles/fiscal-data-package.json').read()
    remote = requests.get('https://specs.frictionlessdata.io/schemas/fiscal-data-package.json').text
    assert local == remote, 'run `make profiles` to update profiles'

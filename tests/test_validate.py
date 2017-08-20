 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from datapackage import validate, exceptions


# Tests

def test_validate_valid():
    valid = validate('data/datapackage/datapackage.json')
    assert valid


def test_validate_invalid():
    with pytest.raises(exceptions.ValidationError) as excinfo:
        validate({})
    assert len(excinfo.value.errors) == 1
    assert 'resources' in str(excinfo.value.errors[0])

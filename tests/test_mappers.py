# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from importlib import import_module
module = import_module('datapackage.mappers')


# Tests

def test_convert_path():
    assert module.convert_path('path.csv', 'name') == 'path___name'
    assert module.convert_path('dir/path.csv', 'name') == 'dir__path___name'
    assert module.convert_path('path.csv', 'Some Name') == 'path___some_name'


def test_restore_path():
    assert module.restore_path('path___name') == ('path.csv', 'name')
    assert module.restore_path('dir__path___name') == ('dir/path.csv', 'name')
    assert module.restore_path('path___some_name') == ('path.csv', 'some_name')

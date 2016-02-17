# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import csv


_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)
is_py33 = (is_py3 and _ver[1] == 3)
is_py34 = (is_py3 and _ver[1] == 4)
is_py27 = (is_py2 and _ver[1] == 7)


if is_py2:
    import urlparse as parse
    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)

    def csv_dict_reader(data, dialect=csv.excel, **kwargs):
        '''Read text stream as CSV, yielding dict objects'''
        dict_reader = csv.DictReader(data, **kwargs)
        for row in dict_reader:
            yield {key: unicode(value, 'utf-8')
                   for key, value in row.iteritems()}

elif is_py3:
    from urllib import parse
    csv_dict_reader = csv.DictReader
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)

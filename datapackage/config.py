# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# Module API

TABULAR_FORMATS = ['csv', 'tsv', 'xls', 'xlsx']
DEFAULT_DATA_PACKAGE_PROFILE = 'data-package'
DEFAULT_RESOURCE_PROFILE = 'data-resource'
DEFAULT_RESOURCE_ENCODING = 'utf-8'
DEFAULT_FIELD_TYPE = 'string'
DEFAULT_FIELD_FORMAT = 'default'
DEFAULT_MISSING_VALUES = ['']
DEFAULT_DIALECT = {
    'delimiter': ',',
    'doubleQuote': True,
    'lineTerminator': '\r\n',
    'quoteChar': '"',
    'skipInitialSpace': True,
    'header': True,
    'caseSensitiveHeader': False,
}

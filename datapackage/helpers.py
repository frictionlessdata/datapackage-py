# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from . import config


# Apply defaults

def apply_defaults_to_data_package(descriptor):
    """Apply defaults to Data Package descriptor (IN-PLACE FOR NOW).
    """
    descriptor.setdefault('profile', config.DEFAULT_DATA_PACKAGE_PROFILE)
    for resource in descriptor.get('resources', []):
        apply_defaults_to_resource(resource)


def apply_defaults_to_resource(descriptor):
    """Apply defaults to Resource descriptor (IN-PLACE FOR NOW).
    """
    descriptor.setdefault('profile', config.DEFAULT_RESOURCE_PROFILE)
    descriptor.setdefault('encoding', config.DEFAULT_RESOURCE_ENCODING)
    if descriptor['profile'] == 'tabular-data-resource':

        # Schema
        schema = descriptor.get('schema')
        if schema is not None:
            for field in schema.get('fields', []):
                field.setdefault('type', config.DEFAULT_FIELD_TYPE)
                field.setdefault('format', config.DEFAULT_FIELD_FORMAT)
            schema.setdefault('missingValues', config.DEFAULT_MISSING_VALUES)

        # Dialect
        dialect = descriptor.get('dialect')
        if dialect is not None:
            for key, value in config.DEFAULT_DIALECT.items():
                dialect.setdefault(key, value)


# Miscellaneous

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
        return False
    if '..%s' % os.path.sep in path:
        return False
    return True

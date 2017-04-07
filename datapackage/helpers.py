# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import six
import json
import requests
import jsonpointer
from . import config
from . import exceptions


# Dereference

def dereference_data_package(descriptor, base_path):
    """Dereference data package descriptor (IN-PLACE FOR NOW).
    """
    for resource in descriptor.get('resources', []):
        dereference_resource(resource, base_path, descriptor)
    return descriptor


def dereference_resource(descriptor, base_path, base_descriptor=None):
    """Dereference resource descriptor (IN-PLACE FOR NOW).
    """
    PROPERTIES = ['schema', 'dialect']
    if base_descriptor is None:
        base_descriptor = descriptor
    for property in PROPERTIES:
        value = descriptor.get(property)

        # URI -> No
        if not isinstance(value, six.string_types):
            continue

        # URI -> Pointer
        if value.startswith('#'):
            try:
                pointer = jsonpointer.JsonPointer(value[1:])
                descriptor[property] = pointer.resolve(base_descriptor)
            except Exception as exception:
                raise exceptions.DataPackageException(
                    'Not resolved Pointer URI "%s" '
                    'for resource.%s' % (value, property))

        # URI -> Remote
        elif value.startswith('http'):
            try:
                response = requests.get(value)
                response.raise_for_status()
                descriptor[property] = response.json()
            except Exception as exception:
                raise exceptions.DataPackageException(
                    'Not resolved Remote URI "%s" '
                    'for resource.%s' % (value, property))

        # URI -> Local
        else:
            if not is_safe_path(value):
                raise exceptions.DataPackageException(
                    'Not safe path in Local URI "%s" '
                    'for resource.%s' % (value, property))
            fullpath = os.path.join(base_path, value)
            try:
                with io.open(fullpath, encoding='utf-8') as file:
                    descriptor[property] = json.load(file)
            except Exception as exception:
                raise exceptions.DataPackageException(
                    'Not resolved Local URI "%s" '
                    'for resource.%s' % (value, property))

    return descriptor


# Apply defaults

def apply_defaults_to_data_package(descriptor):
    """Apply defaults to data package descriptor (IN-PLACE FOR NOW).
    """
    descriptor.setdefault('profile', config.DEFAULT_DATA_PACKAGE_PROFILE)
    for resource in descriptor.get('resources', []):
        apply_defaults_to_resource(resource)
    return descriptor


def apply_defaults_to_resource(descriptor):
    """Apply defaults to resource descriptor (IN-PLACE FOR NOW).
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

    return descriptor


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

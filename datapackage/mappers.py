# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import re


# Module API

def convert_path(path, name):
    """Convert resource's path and name to storage's table name.

    Args:
        path (str): resource path
        name (str): resource name

    Returns:
        str: table name

    """
    table = os.path.splitext(path)[0]
    table = table.replace(os.path.sep, '__')
    if name is not None:
        table = '___'.join([table, name])
    table = re.sub('[^0-9a-zA-Z_]+', '_', table)
    table = table.lower()
    return table


def restore_path(table):
    """Restore resource's path and name from storage's table.

    Args:
        table (str): table name

    Returns:
        (str, str): resource path and name

    """
    name = None
    splited = table.split('___')
    path = splited[0]
    if len(splited) == 2:
        name = splited[1]
    path = path.replace('__', os.path.sep)
    path += '.csv'
    return path, name


def convert_schemas(mapping, schemas):
    """Convert schemas to be compatible with storage schemas.

    Foreign keys related operations.

    Args:
        mapping (dict): mapping between resource name and table name
        schemas (list): schemas

    Returns:
        list: converted schemas

    """
    for schema in schemas:
        for fk in schema.get('foreignKeys', []):
            resource = fk['reference']['resource']
            if resource != 'self':
                if resource not in mapping:
                    message = (
                        'Resource "%s" for foreign key "%s" '
                        'doesn\'t exist.' % (resource, fk))
                    raise ValueError(message)
                fk['reference']['resource'] = '<table>'
                fk['reference']['table'] = mapping[resource]
    return schemas


def restore_resources(mapping, resources):
    """Restore schemas from being compatible with storage schemas.

    Foreign keys related operations.

    Args:
        mapping (dict): mapping between table and resource name
        list: resources

    Returns:
        list: restored resources

    """
    for resource in resources:
        schema = resource['schema']
        for fk in schema.get('foreignKeys', []):
            fkresource = fk['reference']['resource']
            if fkresource == '<table>':
                table = fk['reference']['table']
                _, name = restore_path(table)
                del fk['reference']['table']
                fk['reference']['resource'] = name
    return resources

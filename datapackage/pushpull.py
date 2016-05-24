# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import six
import json
import unicodecsv as csv
from copy import deepcopy
from importlib import import_module
from jsontableschema.model import SchemaModel

from . import helpers
from . import mappers
from .datapackage import DataPackage


# Module API

def push_datapackage(descriptor, backend, **backend_options):
    """Push Data Package to storage.

    All parameters should be used as keyword arguments.

    Args:
        descriptor (str): path to descriptor
        backend (str): backend name like `sql` or `bigquery`
        backend_options (dict): backend options mentioned in backend docs

    """

    # Init maps
    tables = []
    schemas = []
    datamap = {}
    mapping = {}

    # Init model
    model = DataPackage(descriptor)

    # Get storage
    plugin = import_module('jsontableschema.plugins.%s' % backend)
    storage = plugin.Storage(**backend_options)

    # Collect tables/schemas/data
    for resource in model.resources:
        name = resource.metadata.get('name', None)
        table = mappers.convert_path(resource.metadata['path'], name)
        schema = resource.metadata['schema']
        data = resource.iter()
        # TODO: review
        def values(schema, data):
            for item in data:
                row = []
                for field in schema['fields']:
                    row.append(item.get(field['name'], None))
                yield tuple(row)
        tables.append(table)
        schemas.append(schema)
        datamap[table] = values(schema, data)
        if name is not None:
            mapping[name] = table
    schemas = mappers.convert_schemas(mapping, schemas)

    # Create tables
    for table in tables:
        if storage.check(table):
            storage.delete(table)
    storage.create(tables, schemas)

    # Write data to tables
    for table in storage.tables:
        if table in datamap:
            storage.write(table, datamap[table])
    return storage


def pull_datapackage(descriptor, name, backend, **backend_options):
    """Pull Data Package from storage.

    All parameters should be used as keyword arguments.

    Args:
        descriptor (str): path where to store descriptor
        name (str): name of the pulled datapackage
        backend (str): backend name like `sql` or `bigquery`
        backend_options (dict): backend options mentioned in backend docs

    """

    # Save datapackage name
    datapackage_name = name

    # Get storage
    plugin = import_module('jsontableschema.plugins.%s' % backend)
    storage = plugin.Storage(**backend_options)

    # Iterate over tables
    resources = []
    for table in storage.tables:

        # Prepare
        schema = storage.describe(table)
        base = os.path.dirname(descriptor)
        path, name = mappers.restore_path(table)
        fullpath = os.path.join(base, path)

        # Write data
        helpers.ensure_dir(fullpath)
        with io.open(fullpath, 'wb') as file:
            model = SchemaModel(deepcopy(schema))
            data = storage.read(table)
            writer = csv.writer(file, encoding='utf-8')
            writer.writerow(model.headers)
            for row in data:
                writer.writerow(row)

        # Add resource
        resource = {'schema': schema, 'path': path}
        if name is not None:
            resource['name'] = name
        resources.append(resource)

    # Write descriptor
    mode = 'w'
    encoding = 'utf-8'
    if six.PY2:
        mode = 'wb'
        encoding = None
    resources = mappers.restore_resources(resources)
    helpers.ensure_dir(descriptor)
    with io.open(descriptor,
                 mode=mode,
                 encoding=encoding) as file:
        descriptor = {
            'name': datapackage_name,
            'resources': resources,
        }
        json.dump(descriptor, file, indent=4)
    return storage

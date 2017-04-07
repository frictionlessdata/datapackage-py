from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from jsontableschema import Table
from six.moves.urllib.parse import urljoin
from . import exceptions
from . import helpers


# Module API

class Resource(object):
    """Data Resource representation.

    Arguments:
        descriptor (str/dict): VALID Data Resource descriptor
        base_path (str): base path to resolve relative paths

    Raises:
        exceptions.DataPackageException

    Descriptor processing:
        - retrieve
        - dereference
        - expand

    After all this actions will take place the descriptor
    will be available as `resource.descriptor`.

    """

    # Public

    def __init__(self, descriptor, base_path=None):

        # Get base path
        if base_path is None:
            base_path = helpers.get_descriptor_base_path(descriptor)

        # Process descriptor
        descriptor = helpers.retrieve_descriptor(descriptor)
        descriptor = helpers.dereference_resource_descriptor(descriptor, base_path)
        descriptor = helpers.expand_resource_descriptor(descriptor)

        # Get source/source_type
        source, source_type = _get_source_with_type(
            descriptor.get('data'), descriptor.get('path'), base_path)

        # Set attributes
        self.__source_type = source_type
        self.__descriptor = descriptor
        self.__base_path = base_path
        self.__source = source

    @property
    def descriptor(self):
        """dict: resource descriptor
        """
        return self.__descriptor

    @property
    def source_type(self):
        """str: data source type

        Source types:
            - inline
            - local
            - remote
            - multipart-local
            - multipart-remote

        """
        return self.__source_type

    @property
    def source(self):
        """any/str/str[0]: normalized data source

        Based on resource type:
            - inline -> data (any)
            - local/remote -> path[0] (str)
            - multipart-local/multipart-remote -> path (str[])

        Example:

        ```
        if resource.source_type == 'local':
            open(resource.source, mode='rb').read()
        elif resource.source_type == 'remote':
            requests.get(resource.source).text
        elif resource.source_type.startswith('multipart'):
            # logic to handle list of chunks
        ```

        """
        return self.__source

    @property
    def table(self):
        """None/tableschema.Table: provide Table API for tabular resource
        """
        source = self.source

        # Non tabular resource
        if self.descriptor['profile'] != 'tabular-data-resource':
           return None

        # Multipart local resource
        if self.source_type == 'multipart-local':
            # TODO: implement
            source = source

        # Multipart remote resource
        elif self.source_type == 'multipart-remote':
            # TODO: implement
            source = source

        schema = self.descriptor['schema']
        options = _get_table_options(self.descriptor)
        table = Table(source, schema, **options)
        return table


# Internal

_DIALECT_KEYS = [
    'delimiter',
    'doubleQuote',
    'lineTerminator',
    'quoteChar',
    'escapeChar',
    'skipInitialSpace',
]


def _get_source_with_type(data, path, base_path):

    # Inline
    if data is not None:
        source = data
        source_type = 'inline'

    # Local/Remote
    elif len(path) == 1:
        if path[0].startswith('http'):
            source = path[0]
            source_type = 'remote'
        elif base_path and base_path.startswith('http'):
            source = urljoin(base_path, path[0])
            source_type = 'remote'
        else:
            if not helpers.is_safe_path(path[0]):
                raise exceptions.DataPackageException(
                    'Local path "%s" is not safe' % path[0])
            if not base_path:
                raise exceptions.DataPackageException(
                    'Local path "%s" requires base path' % path[0])
            source = os.path.join(base_path, path[0])
            source_type = 'local'

    # Multipart Local/Remote
    elif len(path) > 1:
        source = []
        source_type = 'multipart-local'
        for chunk_path in path:
            chunk_source, chunk_source_type = _get_source_with_type(
                None, [chunk_path], base_path)
            source.append(chunk_source)
            if chunk_source_type == 'remote':
                source_type = 'multipart-remote'

    return source, source_type


def _get_table_options(descriptor):

    # General
    options = {}
    if not descriptor.get('data'):
        options['format'] = 'csv'
    options['encoding'] = descriptor['encoding']

    # Dialect
    dialect = descriptor.get('dialect')
    if dialect:
        for key in _DIALECT_KEYS:
            options[key.lower()] = dialect[key]

    return options

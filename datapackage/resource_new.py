from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsontableschema import Table
from . import helpers


# Module API

class Resource(object):
    """Data Resource representation.

    Arguments:
        descriptor (str/dict): VALID Data Resource descriptor
        base_path (str): base path to resolve relative paths

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

        # Set attributes
        self.__descriptor = descriptor
        self.__base_path = base_path

    @property
    def descriptor(self):
        """dict: resource descriptor
        """
        return self.__descriptor

    @property
    def type(self):
        """str: resource type

        Resource types:
            - inline
            - local
            - remote
            - multipart-local
            - multipart-remote

        """
        data = self.descriptor.get('data')
        path = self.descriptor.get('path')
        # Inline
        if data is not None:
            return 'inline'
        # Local/Remote
        if len(path) == 1:
            if path[0].startswith('http'):
                return 'local'
            else:
                return 'remote'
        # Multipart Local/Remote
        if len(path) > 1:
            if path[0].startswith('http'):
                return 'multipart-local'
            else:
                return 'multipart-remote'

    @property
    def source(self):
        """any/str/str[0]: normalized data source

        Based on resource type:
            - inline -> data (any)
            - local/remote -> path[0] (str)
            - multipart-local/multipart-remote -> path (str[])

        Example:

        ```
        if resource.type == 'local':
            open(resource.source, mode='rb').read()
        elif resource.type == 'remote':
            requests.get(resource.source).text
        elif resource.type.startswith('multipart'):
            # use logic to handle list of chunks
        ```

        """
        if self.type == 'inline':
            return self.descriptor['data']
        if self.type in ['local', 'remote']:
            return self.descriptor['path'][0]
        if self.type in ['multipart-local', 'multipart-remote']:
            return self.descriptor['path']

    @property
    def table(self):
        """None/tableschema.Table: provide Table API for tabular resource
        """
        source = self.source

        # Non tabular resource
        if self.descriptor['profile'] != 'tabular-data-resource':
           return None

        # Multipart local resource
        if self.type == 'multipart-local':
            # TODO: implement
            source = source

        # Multipart remote resource
        elif self.type == 'multipart-remote':
            # TODO: implement
            source = source

        schema = self.descriptor['schema']
        options = _get_table_options(self.descriptor)
        table = Table(source, schema, **options)
        return table


# Internal

def _get_table_options(descriptor):
    DIALECT_KEYS = [
        'delimiter',
        'doubleQuote',
        'lineTerminator',
        'quoteChar',
        'escapeChar',
        'skipInitialSpace',
    ]
    options = {}
    options['format'] = 'csv'
    options['encoding'] = descriptor['encoding']
    dialect = descriptor.get('dialect')
    if dialect:
        for key in DIALECT_KEYS:
            options[key.lower()] = dialect[key]
    return options

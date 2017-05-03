from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
from tableschema import Table
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import urlopen
from . import exceptions
from . import helpers


# Module API

class Resource(object):
    """Data Resource representation.

    Provided descriptor must be valid. For non valid descriptor
    the class behaviour is undefined.

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
    is available as `resource.descriptor`.

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
    def name(self):
        """dict: resource name
        """
        return self.__descriptor['name']

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

        Example:
        ```
        if resource.table:
            resource.schema
            resource.iter()
            resource.read(keyed=True)
            resource.save('table.csv')
        ```

        Reference:
            https://github.com/frictionlessdata/tableschema-py#table

        """

        # Resource -> Regular
        if self.descriptor['profile'] != 'tabular-data-resource':
            return None

        # Resource -> Tabular
        source = self.source
        if self.source_type.startswith('multipart'):
            source = _MultipartSource(self.source, self.source_type)
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
    options['format'] = 'csv'
    if descriptor.get('data'):
        options['format'] = 'native'
    options['encoding'] = descriptor['encoding']
    options['skip_rows'] = descriptor.get('skipRows', [])

    # Dialect
    dialect = descriptor.get('dialect')
    if dialect:
        if not dialect['header']:
            options['headers'] = None
        for key in _DIALECT_KEYS:
            options[key.lower()] = dialect[key]

    return options


class _MultipartSource(object):

    # Public

    def __init__(self, source, source_type):
        self.__source = source
        self.__source_type = source_type
        self.__rows = self.__iter_rows()

    def __iter__(self):
        return self.__rows

    @property
    def closed(self):
        return False

    def readable(self):
        return True

    def seekable(self):
        return True

    def writable(self):
        return False

    def flush(self):
        pass

    def read1(self, size):
        return self.read(size)

    def seek(self, offset):
        assert offset == 0
        self.__rows = self.__iter_rows()

    def read(self, size):
        res = b''
        while True:
            try:
                res += next(self.__rows)
            except StopIteration:
                break
            if len(res) > size:
                break
        return res

    # Private

    def __iter_rows(self):
        streams = []
        if self.__source_type == 'multipart-local':
            streams = [io.open(chunk, 'rb') for chunk in self.__source]
        elif self.__source_type == 'multipart-remote':
            streams = [urlopen(chunk) for chunk in self.__source]
        for stream in streams:
            for row in stream:
                if not row.endswith(b'\n'):
                    row += b'\n'
                yield row

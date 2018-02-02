from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import six
import json
import warnings
import cchardet
from copy import deepcopy
from tableschema import Table, Storage
from six.moves.urllib.parse import urljoin
from six.moves.urllib.request import urlopen
from .profile import Profile
from . import exceptions
from . import helpers
from . import config


# Module API

class Resource(object):
    '''A Data Package Resource.

    Args:
        descriptor (Union[str, dict], optional): Resource descriptor as a local
            path, URL, or dict.
        base_path (str, optional): Base path to be used for all relative paths.
            By default, takes the base path of the descriptor if possible.
        strict (bool, optional): When `True`, errors are raised as soon as
            they're detected. Otherwise you have to manually check for errors
            via the `valid()` and `errors()` methods.
        storage (Union[str, `tableschema.Storage`], optional): Storage name
            (e.g. 'sql') or instance.
        package (`Package`, optional): The data package this resource belongs to.
        **options (dict, optional): Extra options passed to the `storage`.

    Returns:
        `Resource`: The resource object.

    Raises:
        `exceptions.DataPackageException`: Something went wrong.
    '''

    # Public

    def __init__(self, descriptor={}, base_path=None, strict=False, storage=None,
                 # Internal
                 package=None, **options):
        # Get base path
        if base_path is None:
            base_path = helpers.get_descriptor_base_path(descriptor)

        # Instantiate storage
        if storage and not isinstance(storage, Storage):
            storage = Storage.connect(storage, **options)

        # Process descriptor
        descriptor = helpers.retrieve_descriptor(descriptor)
        descriptor = helpers.dereference_resource_descriptor(descriptor, base_path)

        # Handle deprecated resource.path.url
        if descriptor.get('url'):
            warnings.warn(
                'Resource property "url: <url>" is deprecated. '
                'Please use "path: <url>" instead.',
                UserWarning)
            descriptor['path'] = descriptor['url']
            del descriptor['url']

        # Set attributes
        self.__current_descriptor = deepcopy(descriptor)
        self.__next_descriptor = deepcopy(descriptor)
        self.__base_path = base_path
        self.__package = package
        self.__storage = storage
        self.__relations = None
        self.__strict = strict
        self.__table = None
        self.__errors = []

        # Build resource
        self.__build()

    @property
    def valid(self):
        '''Boolean describing if the resource is valid or not.'''
        return not bool(self.__errors)

    @property
    def errors(self):
        '''List of validation errors, if any.'''
        return self.__errors

    @property
    def profile(self):
        '''Returns the resource's `Profile` instance.'''
        return self.__profile

    @property
    def descriptor(self):
        '''Returns the data package descriptor as a `dict`.'''
        # Never use self.descriptor inside self class (!!!)
        return self.__next_descriptor

    @property
    def name(self):
        return self.__current_descriptor.get('name')

    @property
    def inline(self):
        return self.__source_inspection.get('inline', False)

    @property
    def local(self):
        return self.__source_inspection.get('local', False)

    @property
    def remote(self):
        return self.__source_inspection.get('remote', False)

    @property
    def multipart(self):
        return self.__source_inspection.get('multipart', False)

    @property
    def tabular(self):
        if self.__current_descriptor.get('profile') == 'tabular-data-resource':
            return True
        if not self.__strict:
            if self.__current_descriptor.get('format') in config.TABULAR_FORMATS:
                return True
            if self.__source_inspection.get('tabular', False):
                return True
        return False

    @property
    def source(self):
        return self.__source_inspection.get('source')

    @property
    def headers(self):
        '''Tabular resource only. The headers list.'''
        if not self.tabular:
            return None
        return self.__get_table().headers

    @property
    def schema(self):
        '''Tabular resource only. The `tableschema.Schema` instance if it exists.'''
        if not self.tabular:
            return None
        return self.__get_table().schema

    def iter(self, keyed=False, extended=False, cast=True, relations=False):
        '''Tabular resource only. Iterates over the tabular resource's rows.

        There are three formats of returning the rows, the default, keyed, and
        extended. Consider a CSV as:

            name,value
            J Doe,10

        This will be returned as:

        * Default: `['J Doe', 10]`
        * Keyed: `{'name': 'J Doe', 'value': 10}`
        * Extended: `(1, ['name', 'value'], ['J Doe', 10])`

        Notice that you can only set a single format at a time. The behaviour
        of `iter(keyed=True, extended=True)` is undefined.

        Args:
            keyed (bool, optional): When `True`, each returned row will be a
                `dict` mapping the header name to its value in the current row.
                For example, `[{'name': 'J Smith', 'value': '10'}]`. Ignored if
                ``extended`` is True. Defaults to False.
            extended (bool, optional): When `True`, returns each row as a tuple
                with row number (starts at 1), list of headers, and list of row
                values. For example, `(1, ['name', 'value'], ['J Smith', '10'])`.
                Defaults to False.
            cast (bool, optional): When `True`, casts the cell values according
                to the `schema()`. Defaults to `True`.
            relations (bool, optional): When `True`, check and resolve foreign
                keys, adding their contents to the returned rows. Defaults to
                `False`.

        Yields:
            Union[List[Any], Dict[str, Any], Tuple[int, List[str], List[Any]]]:
                The rows themselves. The format depends on the values of
                `keyed` and `extended` arguments.

        Raises:
            `exceptions.DataPackageException`: Something went wrong.
        '''

        # Error for non tabular
        if not self.tabular:
            message = 'Methods iter/read are not supported for non tabular data'
            raise exceptions.DataPackageException(message)

        # Get relations
        if relations:
            relations = self.__get_relations()

        return self.__get_table().iter(
            keyed=keyed,
            extended=extended,
            cast=cast,
            relations=relations
        )

    def read(self, keyed=False, extended=False, cast=True, relations=False, limit=None):
        '''Tabular resource only. Iterates over the tabular resource's rows.

        There are three formats of returning the rows, the default, keyed, and
        extended. Consider a CSV as:

            name,value
            J Doe,10

        This will be returned as:

        * Default: `['J Doe', 10]`
        * Keyed: `{'name': 'J Doe', 'value': 10}`
        * Extended: `(1, ['name', 'value'], ['J Doe', 10])`

        Notice that you can only set a single format at a time. The behaviour
        of `read(keyed=True, extended=True)` is undefined.

        Args:
            keyed (bool, optional): When `True`, each returned row will be a
                `dict` mapping the header name to its value in the current row.
                For example, `[{'name': 'J Smith', 'value': '10'}]`. Ignored if
                ``extended`` is True. Defaults to False.
            extended (bool, optional): When `True`, returns each row as a tuple
                with row number (starts at 1), list of headers, and list of row
                values. For example, `(1, ['name', 'value'], ['J Smith', '10'])`.
                Defaults to False.
            cast (bool, optional): When `True`, casts the cell values according
                to the `schema()`. Defaults to `True`.
            relations (bool, optional): When `True`, check and resolve foreign
                keys, adding their contents to the returned rows. Defaults to
                `False`.
            limit (int, optional): Maximum number of rows to return. Defaults
                to `None`, i.e. returns all rows.

        Returns:
            List[Union[List[Any], Dict[str, Any], Tuple[int, List[str], List[Any]]]]:
                The rows themselves. The format depends on the values of
                `keyed` and `extended` arguments.

        Raises:
            `exceptions.DataPackageException`: Something went wrong.
        '''

        # Error for non tabular
        if not self.tabular:
            message = 'Methods iter/read are not supported for non tabular data'
            raise exceptions.DataPackageException(message)

        # Get relations
        if relations:
            relations = self.__get_relations()

        return self.__get_table().read(
            keyed=keyed,
            extended=extended,
            cast=cast,
            relations=relations,
            limit=limit
        )

    def check_relations(self):
        '''Tabular resource only. Validate foreign key relations.

        Returns:
            bool: `True` if there are no issues.

        Raises:
            `exceptions.RelationError`: If there is any integrity relations
                issue (e.g. an unknown foreign key).
        '''
        [row for row in self.iter(relations=True)]
        return True

    def raw_iter(self):
        '''Returns file-like object that iterates over resource as a binary stream.

        Can't be used with inline resources.

        Returns:
            BinaryIO: File-like object opened as binary.

        Raises:
            `exceptions.DataPackageException`: If called on a inline resource.
        '''

        # Error for inline
        if self.inline:
            message = 'Methods raw_iter/raw_read are not supported for inline data'
            raise exceptions.DataPackageException(message)

        # Get filelike
        if self.multipart:
            filelike = _MultipartSource(self.source, remote=self.remote)
        elif self.remote:
            filelike = urlopen(self.source)
        else:
            filelike = io.open(self.source, 'rb')

        return filelike

    def raw_read(self):
        '''Returns resource contents as bytes.

        Can't be used with inline resources.

        Returns:
            ByteString: Binary resource contents.

        Raises:
            `exceptions.DataPackageException`: If called on a inline resource.
        '''

        fp = self.raw_iter()
        contents = b''.join([chunk for chunk in fp])
        fp.close()
        return contents

    def infer(self):
        '''Infer and commit this resource's metadata.'''
        descriptor = deepcopy(self.__current_descriptor)

        # Blank -> Stop
        if self.__source_inspection.get('blank'):
            return descriptor

        # Name
        if not descriptor.get('name'):
            descriptor['name'] = self.__source_inspection['name']

        # Only for non inline/storage
        if not self.inline and not self.__storage:

            # Format
            if not descriptor.get('format'):
                descriptor['format'] = self.__source_inspection['format']

            # Mediatype
            if not descriptor.get('mediatype'):
                descriptor['mediatype'] = 'text/%s' % descriptor['format']

            # Encoding
            if descriptor.get('encoding') == config.DEFAULT_RESOURCE_ENCODING:
                contents = b''
                with self.raw_iter(stream=True) as stream:
                    for chunk in stream:
                        contents += chunk
                        if len(contents) > 1000: break
                encoding = cchardet.detect(contents)['encoding'].lower()
                descriptor['encoding'] = 'utf-8' if encoding == 'ascii' else encoding

        # Schema
        if not descriptor.get('schema'):
            if self.tabular:
                descriptor['schema'] = self.__get_table().infer()

        # Profile
        if descriptor.get('profile') == config.DEFAULT_RESOURCE_PROFILE:
            if self.tabular:
                descriptor['profile'] = 'tabular-data-resource'

        # Save descriptor
        self.__current_descriptor = descriptor
        self.__build()

        return descriptor

    def commit(self, strict=None):
        '''Commits any changes to the descriptor.

        Args:
            strict (bool, optional): If set, enables or disables this resource's
                strict mode.

        Returns:
            bool: `True` if there were changes commited, `False` if nothing was
                modified (because there were no modifications to be made).

        Raises:
            `exceptions.DataPackageException`: Something went wrong.
        '''
        if strict is not None:
            self.__strict = strict
        elif self.__current_descriptor == self.__next_descriptor:
            return False
        self.__current_descriptor = deepcopy(self.__next_descriptor)
        self.__table = None
        self.__build()
        return True

    def save(self, target, storage=None, **options):
        '''Saves data resource.

        If the `storage` is `None`, this will save this resource's descriptor
        only. Otherwise it will save the descriptor and data to `storage`.

        Args:
            target (str): Target path to save the resource descriptor.
            storage (tableschema.Storage, optional): Storage instance to save
                the data package into.
            **options (dict, optional): Options to pass to the `storage` instance.

        Returns:
            bool: `True` when successful.

        Raises:
            `exceptions.DataPackageException`: Something went wrong.
        '''

        # Save resource to storage
        if storage is not None:
            if self.tabular:
                self.infer()
                storage.create(target, self.schema.descriptor, force=True)
                storage.write(target, self.iter())

        # Save descriptor to json
        else:
            mode = 'w'
            encoding = 'utf-8'
            if six.PY2:
                mode = 'wb'
                encoding = None
            helpers.ensure_dir(target)
            with io.open(target, mode=mode, encoding=encoding) as file:
                json.dump(self.__current_descriptor, file, indent=4)

        return True

    # Private

    def __build(self):

        # Process descriptor
        expand = helpers.expand_resource_descriptor
        self.__current_descriptor = expand(self.__current_descriptor)
        self.__next_descriptor = deepcopy(self.__current_descriptor)

        # Inspect source
        self.__source_inspection = _inspect_source(
            self.__current_descriptor.get('data'),
            self.__current_descriptor.get('path'),
            self.__base_path,
            self.__storage)

        # Instantiate profile
        self.__profile = Profile(self.__current_descriptor.get('profile'))

        # Validate descriptor
        try:
            self.__profile.validate(self.__current_descriptor)
            self.__errors = []
        except exceptions.ValidationError as exception:
            self.__errors = exception.errors
            if self.__strict:
                raise exception

    def __get_table(self):
        if not self.__table:

            # Non tabular -> None
            if not self.tabular:
                return None

            # Get source/schema
            source = self.source
            if self.multipart:
                source = _MultipartSource(self.source, remote=self.remote)
            schema = self.descriptor.get('schema')

            # Storage resource
            if self.__storage is not None:
                self.__table = Table(source, schema=schema, storage=self.__storage)

            # General resource
            else:
                options = {}
                descriptor = self.__current_descriptor
                options['format'] = descriptor.get('format', 'csv')
                if descriptor.get('data'):
                    options['format'] = 'inline'
                options['encoding'] = descriptor['encoding']
                options['skip_rows'] = descriptor.get('skipRows', [])
                dialect = descriptor.get('dialect')
                if dialect:
                    if not dialect.get('header', config.DEFAULT_DIALECT['header']):
                        fields = descriptor.get('schema', {}).get('fields', [])
                        options['headers'] = [field['name'] for field in fields] or None
                    for key in _DIALECT_KEYS:
                        if key in dialect:
                            options[key.lower()] = dialect[key]
                self.__table = Table(source, schema=schema, **options)

        return self.__table

    def __get_relations(self):
        if not self.__relations:

            # Prepare resources
            resources = {}
            if self.__get_table() and self.__get_table().schema:
                for fk in self.__get_table().schema.foreign_keys:
                    resources.setdefault(fk['reference']['resource'], [])
                    for field in fk['reference']['fields']:
                        resources[fk['reference']['resource']].append(field)

            # Fill relations
            self.__relations = {}
            for resource, fields in resources.items():
                if resource and not self.__package:
                    continue
                self.__relations.setdefault(resource, [])
                data = self.__package.get_resource(resource) if resource else self
                if data.tabular:
                    self.__relations[resource] = data.read(keyed=True)

        return self.__relations

    # Deprecated

    @property
    def table(self):
        """Return resource table
        """

        # Deprecate
        warnings.warn(
            'Property "resource.table" is deprecated. '
            'Please use "resource.iter/read" directly.',
            UserWarning)

        return self.__get_table()

    @property
    def data(self):
        """Return resource data
        """

        # Deprecate
        warnings.warn(
            'Property "resource.data" is deprecated. '
            'Please use "resource.read(keyed=True)" instead.',
            UserWarning)

        return self.read(keyed=True)


# Internal

_DIALECT_KEYS = [
    'delimiter',
    'doubleQuote',
    'lineTerminator',
    'quoteChar',
    'escapeChar',
    'skipInitialSpace',
]


def _inspect_source(data, path, base_path, storage):
    inspection = {}

    # Normalize path
    if path and not isinstance(path, list):
        path = [path]

    # Blank
    if not data and not path:
        inspection['source'] = None
        inspection['blank'] = True

    # Storage
    elif storage is not None:
        inspection['name'] = path[0]
        inspection['source'] = path[0]
        inspection['tabular'] = True

    # Inline
    elif data is not None:
        inspection['name'] = 'inline'
        inspection['source'] = data
        inspection['inline'] = True
        inspection['tabular'] = isinstance(data, list)

    # Local/Remote
    elif len(path) == 1:

        # Remote
        if path[0].startswith('http'):
            inspection['source'] = path[0]
            inspection['remote'] = True
        elif base_path and base_path.startswith('http'):
            norm_base_path = base_path if base_path.endswith('/') else base_path + '/'
            inspection['source'] = urljoin(norm_base_path, path[0])
            inspection['remote'] = True

        # Local
        else:

            # Path is not safe
            if not helpers.is_safe_path(path[0]):
                raise exceptions.DataPackageException(
                    'Local path "%s" is not safe' % path[0])

            # Not base path
            if not base_path:
                raise exceptions.DataPackageException(
                    'Local path "%s" requires base path' % path[0])

            inspection['source'] = os.path.join(base_path, path[0])
            inspection['local'] = True

        # Inspect
        filename = os.path.basename(path[0])
        inspection['format'] = os.path.splitext(filename)[1][1:]
        inspection['name'] = os.path.splitext(filename)[0]
        inspection['tabular'] = inspection['format'] in config.TABULAR_FORMATS

    # Multipart Local/Remote
    elif len(path) > 1:
        inspections = list(map(lambda item: _inspect_source(None, item, base_path, None), path))
        inspection.update(inspections[0])
        inspection['source'] = list(map(lambda item: item['source'], inspections))
        inspection['multipart'] = True

    return inspection


class _MultipartSource(object):

    # Public

    def __init__(self, source, remote=False):
        self.__source = source
        self.__remote = remote
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

    def close(self):
        pass

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
        if self.__remote:
            streams = [urlopen(chunk) for chunk in self.__source]
        else:
            streams = [io.open(chunk, 'rb') for chunk in self.__source]
        for stream in streams:
            for row in stream:
                if not row.endswith(b'\n'):
                    row += b'\n'
                yield row

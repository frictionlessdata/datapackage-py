from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import os
import csv
import json
import six
import tabulator
import tabulator.processors

from .resource_file import (
    InlineResourceFile,
    LocalResourceFile,
    RemoteResourceFile,
)
from .exceptions import (
    ResourceError
)


class Resource(object):
    '''Base class for all Data Package's resource types.

    This classes will usually be created by :class:`DataPackage`, and not by
    you. If you need to create one, use the :func:`Resource.load` factory
    method.

    The resources' attributes should only be altered through the
    :data:`metadata` dict.
    '''

    @classmethod
    def load(cls, metadata, default_base_path=None):
        '''Factory method that loads the resource described in ``metadata``.

        It'll first try to load the resource defined in ``metadata`` as a
        :class:`TabularResource`. If that fails, it'll fall back to loading it
        as a :class:`Resource`.

        Args:
            metadata (dict): The dict with the resource's metadata
            default_base_path (str, optional): The base path to be used in case
                the resource's data is in the local disk. Usually this would be
                the base path of the `datapackage.json` this resource is in.

        Returns:
            Resource: The returned resource's class will depend on the type of
                resource. If it was tabular, a :class:`TabularResource` will be
                returned, otherwise, it'll be a :class:`Resource`.

        Raises:
            ResourceError: If the resource couldn't be loaded.
        '''
        if TabularResource.can_handle(metadata):
            resource_class = TabularResource
        else:
            resource_class = Resource

        return resource_class(metadata, default_base_path)

    def __init__(self, metadata, default_base_path=None):
        self._metadata = metadata
        self._base_path = self.metadata.get('base', default_base_path)

    @property
    def metadata(self):
        '''dict: The metadata this resource was created with.'''
        return self._metadata

    @property
    def data(self):
        '''Returns this resource's data.

        The data should not be changed.

        Returns:
            bytes or data's type: This resource's data. If the data was
                inlined, the return type will have the data's type. If not,
                it'll be bytes.

        Raises:
            ResourceError: If the data couldn't be loaded.
        '''
        if not hasattr(self, '_data') or \
           self._metadata_data_has_changed(self.metadata):
            self._data = self._parse_data(self.metadata)
        return self._data

    @property
    def local_data_path(self):
        '''str: The absolute local path for the data.'''
        path = self._absolute_path(self.metadata.get('path'))
        if path:
            return os.path.abspath(path)

    @property
    def remote_data_path(self):
        '''str: The remote path for the data, if it exists.

        The URL will only be returned if it has a scheme (e.g. http, https,
        etc.) by itself or when considering the datapackage's or resource's
        base path.
        '''
        url = self.metadata.get('url')
        if url:
            return url
        else:
            path = self._absolute_path(self.metadata.get('path'))
            if path and _is_url(path):
                return path

    @property
    def _resource_file(self):
        if self._metadata_data_has_changed(self.metadata):
            resource_file = self._load_resource_file()
        else:
            try:
                resource_file = self.__resource_file
            except AttributeError:
                resource_file = self._load_resource_file()

        self.__resource_file = resource_file
        return self.__resource_file

    def iter(self):
        '''Lazily-iterates over the data.

        This method is useful when you don't want to load all data in memory at
        once. The returned iterator behaviour depends on the type of the data.

        If it's a string, it'll iterate over rows **without removing the
        newlines**. The returned data type will be bytes, not string. If it's
        any other type, the iterator will simply return it.

        Returns:
            iter: An iterator that yields this resource.

        Raises:
            ValueError: If the data isn't tabular or if the resource has
                no data.
            IOError: If there was some problem opening the data file (e.g. it
                doesn't exist or we don't have permissions to read it).
        '''
        if self._resource_file:
            return iter(self._resource_file)
        else:
            raise ValueError('Resource has no data')

    def _metadata_data_has_changed(self, metadata):
        changed = False
        metadata_data_ids = self._metadata_data_ids(metadata)
        try:
            changed = metadata_data_ids != self._original_metadata_data_ids
        except AttributeError:
            self._original_metadata_data_ids = metadata_data_ids
        return changed

    def _metadata_data_ids(self, metadata):
        return {
            'data_id': id(metadata.get('data')),
            'data_path_id': id(metadata.get('path')),
            'data_url_id': id(metadata.get('url'))
        }

    def _load_resource_file(self):
        inline_data = self.metadata.get('data')
        data_path = self.metadata.get('path')
        data_url = self.metadata.get('url')

        if inline_data:
            return InlineResourceFile(inline_data)
        if self.local_data_path and os.path.isfile(self.local_data_path):
            return LocalResourceFile(self.local_data_path)
        elif self.remote_data_path:
            try:
                return RemoteResourceFile(self.remote_data_path)
            except ResourceError:
                if data_url:
                    return RemoteResourceFile(data_url)
        elif data_url:
            return RemoteResourceFile(data_url)

        if inline_data or data_path or data_url:
            raise ResourceError('Couldn\'t load resource.')

    def _parse_data(self, metadata):
        return self._load_data()

    def _load_data(self):
        if self._resource_file:
            return self._resource_file.read()

    def _absolute_path(self, path):
        if path is None or self._base_path is None:
            return path
        return os.path.join(self._base_path, path)


class TabularResource(Resource):
    '''Subclass of :class:`Resource` that deals with tabular data.

    It currently supports CSV, XLS, XLSX and JSON.
    '''

    @classmethod
    def can_handle(cls, metadata):
        '''bool: Returns True if this class can handle the resource in
        metadata.'''
        TABULAR_RESOURCE_FORMATS = ('csv', 'xls', 'xlsx', 'json')
        get_extension = lambda x: x.split('.')[-1].lower()

        metadata_data = metadata.get('data')
        if metadata_data:
            try:
                cls._raise_if_isnt_tabular_data(metadata_data)
                return True
            except ValueError:
                pass

        metadata_format = metadata.get('format', '').lower()
        metadata_path = metadata.get('path', '')
        metadata_url = metadata.get('url', '')
        if metadata_format in TABULAR_RESOURCE_FORMATS or \
           get_extension(metadata_path) in TABULAR_RESOURCE_FORMATS or \
           get_extension(metadata_url) in TABULAR_RESOURCE_FORMATS:
            return True

        return False

    @staticmethod
    def _raise_if_isnt_tabular_data(data):
        tabular_types = (
            list,
            tuple,
        )
        valid = False

        for tabular_type in tabular_types:
            if isinstance(data, tabular_type):
                valid = True
                break

        if not valid:
            types_str = ', '.join([t.__name__ for t in tabular_types])
            msg = 'Expected data type to be any of \'{0}\' but it was \'{1}\''
            raise ValueError(msg.format(types_str, type(data).__name__))

    def iter(self):
        '''Lazily-iterates over rows in data.

        This method is useful when you don't want to load all data in memory at
        once.

        Returns:
            iter: An iterator that yields each row in this resource.

        Raises:
            ValueError: If the data isn't tabular or if the resource has
                no data.
            IOError: If there was some problem opening the data file (e.g. it
                doesn't exist or we don't have permissions to read it).
        '''
        result = None
        inline_data = self.metadata.get('data')
        if self.local_data_path and os.path.isfile(self.local_data_path):
            data_path_or_url = self.local_data_path
        else:
            data_path_or_url = self.remote_data_path

        if inline_data:
            inline_data = self._parse_inline_data()
            result = iter(inline_data)
        elif data_path_or_url:
            try:
                table = tabulator.topen(data_path_or_url)
                table.add_processor(tabulator.processors.Headers())
                result = table
            except tabulator.errors.Error as e:
                msg = 'Data at \'{0}\' isn\'t in a known tabular data format'
                six.raise_from(ValueError(msg.format(data_path_or_url)), e)

        if result is None:
            if self.metadata.get('path'):
                # FIXME: This is a hack to throw an IOError when local data
                # exists but couldn't be loaded for some reason. If "path"
                # existed and there were no issues opening it, "result" would
                # never be None.
                raise IOError('Resource\'s data couldn\'t be loaded.')

            raise ValueError('Resource has no data')

        return result

    def _load_data(self):
        return [row for row in self.iter()]

    def _parse_inline_data(self):
        data = self.metadata.get('data')

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        if isinstance(data, six.string_types):
            try:
                data = json.loads(data)
            except ValueError:
                data = [row for row in _csv_dictreader(six.StringIO(data))]
                if not data:
                    data = None

        self._raise_if_isnt_tabular_data(data)

        return data


if six.PY2:
    def _csv_dictreader(data, dialect=csv.excel, **kwargs):
        '''Read text stream (unicode on Py2.7) as CSV.'''

        def iterenc_utf8(data):
            for line in data:
                yield line.encode('utf-8')

        reader = csv.DictReader(iterenc_utf8(data), dialect=dialect, **kwargs)
        for row in reader:
            yield dict([(unicode(k, 'utf-8'), unicode(v, 'utf-8'))
                        for (k, v) in row.items()])
else:
    _csv_dictreader = csv.DictReader


def _is_url(path):
    parts = six.moves.urllib.parse.urlsplit(path)
    return bool(parts.scheme and parts.netloc)

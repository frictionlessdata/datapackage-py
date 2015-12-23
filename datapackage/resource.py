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
            self._resource_file = self._load_resource_file()
            self._data = self._parse_data(self.metadata)
        return self._data

    @property
    def local_data_path(self):
        '''str: The absolute local path for the data, if it exists locally.'''
        path = self._absolute_path(self.metadata.get('path'))
        if path and os.path.isfile(path):
            return os.path.abspath(path)

    def iter(self):
        # FIXME: Delegate this to self._resource_file
        pass

    def _metadata_data_has_changed(self, metadata):
        metadata_data_ids = self._metadata_data_ids(metadata)
        return metadata_data_ids != self._original_metadata_data_ids

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
        if self.local_data_path:
            return LocalResourceFile(self.local_data_path)
        elif data_path and self._absolute_path(data_path) != data_path:
            try:
                return RemoteResourceFile(self._absolute_path(data_path))
            except ResourceError:
                if data_url:
                    return RemoteResourceFile(data_url)
        elif data_url:
            return RemoteResourceFile(data_url)

        if inline_data or data_path or data_url:
            raise ResourceError('Couldn\'t load resource.')

    def _parse_data(self, metadata):
        self._original_metadata_data_ids = self._metadata_data_ids(metadata)
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
        '''
        result = None
        inline_data = self.metadata.get('data')
        data_path_or_url = self.metadata.get('path', self.metadata.get('url'))

        if inline_data:
            inline_data = self._parse_inline_data()
            result = iter(inline_data)
        elif data_path_or_url:
            try:
                table = tabulator.topen(data_path_or_url)
                table.add_processor(tabulator.processors.Headers())
                result = table.readrow(with_headers=True)
            except tabulator.errors.Error:
                msg = 'Data at \'{0}\' isn\'t in a known tabular data format'
                raise ValueError(msg.format(data_path_or_url))

        if result is None:
            raise ValueError()

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

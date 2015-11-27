from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import os
import csv
import json
import requests
import six

from .exceptions import (
    ResourceError
)


class Resource(object):
    '''Base class for all Data Package's resource types.

    This classes will usually be created by :class:`DataPackage`, and not by
    you. If you need to create one, use the :func:`Resource.load` factory
    method.
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
        '''
        try:
            resource = TabularResource(metadata, default_base_path)
        except ValueError:
            resource = cls(metadata, default_base_path)
        return resource

    def __init__(self, metadata, default_base_path=None):
        self._metadata = metadata
        self._base_path = self.metadata.get('base', default_base_path)
        self._data = self._parse_data(metadata)

    @property
    def metadata(self):
        '''dict: The metadata this resource was created with.'''
        return self._metadata

    @property
    def data(self):
        '''str: This resource's data.'''
        return self._data

    def _parse_data(self, metadata):
        return self._load_data(metadata)

    def _load_data(self, metadata):
        inline_data = metadata.get('data')
        data_path = metadata.get('path')
        data_url = metadata.get('url')
        data = None

        if inline_data is not None:
            data = inline_data
        elif data_path is not None:
            path = self._absolute_path(data_path)
            try:
                with open(path, 'r') as f:
                    data = f.read()
                    if six.PY2:
                        data = unicode(data, 'utf-8')
            except IOError as e:
                six.raise_from(ResourceError(e), e)
        elif data_url is not None:
            try:
                req = requests.get(data_url)
                req.raise_for_status()
                data = req.text
            except requests.exceptions.RequestException as e:
                six.raise_from(ResourceError(e), e)

        return data

    def _absolute_path(self, path):
        if self._base_path is None:
            return path
        return os.path.join(self._base_path, path)


class TabularResource(Resource):
    '''Subclass of :class:`Resource` that deals with tabular data.

    It currently only supports CSVs.
    '''

    @property
    def data(self):
        '''list: This resource's data.'''
        return super(TabularResource, self).data

    def _parse_data(self, metadata):
        '''Parses the data

        Raises:
            ValueError: If the data isn't tabular. We consider tabular data as
                a ``dict``, ``list``, ``tuple``, ``JSON`` or ``CSV``.
        '''
        data = self._load_data(metadata)

        if isinstance(data, six.string_types):
            try:
                data = json.loads(data)
            except ValueError:
                data = [row for row in _csv_dictreader(six.StringIO(data))]
                if not data:
                    data = None

        if not self._is_tabular_data(data):
            raise ValueError()

        return data

    def _is_tabular_data(self, data):
        return (isinstance(data, dict) or
                isinstance(data, list) or
                isinstance(data, tuple))


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

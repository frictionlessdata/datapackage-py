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
    @classmethod
    def load(cls, data, default_base_path=None):
        try:
            resource = TabularResource(data, default_base_path)
        except ValueError:
            resource = cls(data, default_base_path)
        return resource

    def __init__(self, metadata, default_base_path=None):
        self._metadata = metadata
        self._base_path = self.metadata.get('base', default_base_path)
        self._data = self._parse_data(metadata)

    @property
    def metadata(self):
        return self._metadata

    @property
    def data(self):
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
    def _parse_data(self, metadata):
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
        """Read text stream (unicode on Py2.7) as CSV."""

        def iterenc_utf8(data):
            for line in data:
                yield line.encode('utf-8')

        reader = csv.DictReader(iterenc_utf8(data), dialect=dialect, **kwargs)
        for row in reader:
            yield dict([(unicode(k, 'utf-8'), unicode(v, 'utf-8'))
                        for (k, v) in row.items()])
else:
    _csv_dictreader = csv.DictReader

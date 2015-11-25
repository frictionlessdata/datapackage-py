from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import csv
import json
import requests
import six

from .exceptions import (
    ResourceError
)


class Resource(object):
    @classmethod
    def load(cls, data):
        try:
            resource = TabularResource(data)
        except ValueError:
            resource = cls(data)
        return resource

    def __init__(self, metadata):
        self._metadata = metadata
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
        has_inline_data = lambda resource: resource.get('data') is not None
        has_url_data = lambda resource: resource.get('url') is not None

        data = None

        if has_inline_data(metadata):
            data = metadata.get('data')
        elif has_url_data(metadata):
            try:
                req = requests.get(metadata.get('url'))
                req.raise_for_status()
                data = req.text
            except requests.exceptions.RequestException as e:
                six.raise_from(ResourceError(e), e)

        return data


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

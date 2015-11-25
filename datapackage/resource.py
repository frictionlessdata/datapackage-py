from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import csv
import json
import six


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
        self._data = self.metadata.get('data')

    @property
    def metadata(self):
        return self._metadata

    @property
    def data(self):
        return self._data


class TabularResource(Resource):
    def __init__(self, metadata):
        super(TabularResource, self).__init__(metadata)

        self._data = self._load_data(metadata)

    def _load_data(self, resource_dict):
        has_inline_data = lambda resource: resource.get('data') is not None
        data = None
        if has_inline_data(resource_dict):
            data = self._load_inline_data(resource_dict.get('data'))

        if not self._is_tabular_data(data):
            raise ValueError()

        return data

    def _load_inline_data(self, data):
        the_data = data

        if isinstance(data, six.string_types):
            try:
                the_data = json.loads(data)
            except ValueError:
                the_data = [row for row in _csv_dictreader(six.StringIO(data))]
                if not the_data:
                    the_data = None

        return the_data

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

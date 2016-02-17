 # -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import six
import requests

urlparse = six.moves.urllib.parse.urlparse


class InlineResourceFile(object):
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        data = [self._data]
        if isinstance(self._data, six.binary_type):
            data = io.BytesIO(self._data)
        elif isinstance(self._data, six.string_types):
            data = io.BytesIO(self._data.encode('utf-8'))
        return iter(data)

    def read(self):
        return self._data


class LocalResourceFile(object):
    def __init__(self, path):
        self._file = self._load_file(path)
        self._file_content = None

    def _load_file(self, path):
        return open(path, 'rb')

    def __del__(self):
        if hasattr(self, '_file'):
            self._file.close()

    def __iter__(self):
        return iter(self._file)

    def read(self):
        if self._file_content is None:
            self._file_content = self._file.read()

        return self._file_content


class RemoteResourceFile(object):
    def __init__(self, url):
        self._file = self._load_file(url)
        self._file_content = None

    def _load_file(self, url):
        try:
            res = requests.get(url, stream=True)
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as e:
            six.raise_from(IOError(e), e)

    def __del__(self):
        if hasattr(self, '_file'):
            self._file.close()

    def __iter__(self):
        return iter(self._file.raw)

    def read(self):
        if self._file_content is None:
            self._file_content = self._file.content

        return self._file_content

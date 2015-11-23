from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import six
from .schema import Schema
from .exceptions import (
    DataPackageException
)


class DataPackage(object):
    SCHEMAS_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'schemas'
    )
    BASE_SCHEMA_PATH = os.path.join(SCHEMAS_PATH, 'base.json')

    def __init__(self, data=None, schema=BASE_SCHEMA_PATH):
        self._data = self._load_data(data)
        self._schema = Schema(schema)

    @property
    def data(self):
        return self._data

    @property
    def schema(self):
        return self._schema

    @property
    def attributes(self):
        attributes = set(self.to_dict().keys())
        try:
            attributes.update(self.schema.properties.keys())
        except AttributeError:
            pass
        return list(attributes)

    def to_dict(self):
        return self._data

    def validate(self):
        self.schema.validate(self.to_dict())

    def _load_data(self, data):
        the_data = data

        if the_data is None:
            the_data = {}

        if isinstance(the_data, six.string_types):
            try:
                the_data = json.load(open(data, 'r'))
            except IOError as e:
                msg = 'Unable to load JSON at \'{0}\''.format(data)
                six.raise_from(DataPackageException(msg), e)
        elif not isinstance(the_data, dict):
            msg = 'Unable to load data \'{0}\''.format(data)
            raise DataPackageException(msg)

        return the_data

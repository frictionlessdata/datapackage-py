from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from .schema import Schema


class DataPackage(object):
    SCHEMAS_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'schemas'
    )
    BASE_SCHEMA_PATH = os.path.join(SCHEMAS_PATH, 'base.json')

    def __init__(self, descriptor=None, schema=BASE_SCHEMA_PATH):
        if descriptor is None:
            descriptor = {}
        self.__dict__.update(descriptor)
        self._schema = Schema(schema)

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
        is_private = lambda k: k.startswith('_')

        return {k: v for (k, v) in self.__dict__.items()
                if not is_private(k) and v is not None}

    def validate(self):
        self.schema.validate(self.to_dict())

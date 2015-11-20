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

    def __init__(self, descriptor=None, schema=BASE_SCHEMA_PATH):
        self.__dict__.update(self._load_descriptor(descriptor))
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

    def _load_descriptor(self, descriptor):
        the_descriptor = descriptor

        if the_descriptor is None:
            the_descriptor = {}

        if isinstance(the_descriptor, six.string_types):
            try:
                the_descriptor = json.load(open(descriptor, 'r'))
            except IOError as e:
                msg = 'Unable to load JSON at \'{0}\''.format(descriptor)
                six.raise_from(DataPackageException(msg), e)
        elif not isinstance(the_descriptor, dict):
            msg = 'Unable to load descriptor \'{0}\''.format(descriptor)
            raise DataPackageException(msg)

        return the_descriptor

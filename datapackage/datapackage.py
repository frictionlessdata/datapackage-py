from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import six
import datapackage_registry
from .schema import Schema
from .exceptions import (
    DataPackageException
)


class DataPackage(object):
    def __init__(self, data=None, schema='base'):
        self._data = self._load_data(data)
        self._schema = self._load_schema(schema)
        self._resources = ()

    @property
    def data(self):
        return self._data

    @property
    def schema(self):
        return self._schema

    @property
    def resources(self):
        return self._resources

    @property
    def attributes(self):
        attributes = set(self.to_dict().keys())
        try:
            attributes.update(self.schema.properties.keys())
        except AttributeError:
            pass
        return list(attributes)

    @property
    def required_attributes(self):
        '''Return required attributes or empty list if nothing is required.'''
        required = []
        try:
            if self.schema.required is not None:
                required = self.schema.required
        except AttributeError:
            pass
        return required

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
            except (ValueError, IOError) as e:
                msg = 'Unable to load JSON at \'{0}\''.format(data)
                six.raise_from(DataPackageException(msg), e)
        if not isinstance(the_data, dict):
            msg = 'Data must be a \'dict\', but was a \'{0}\''
            raise DataPackageException(msg.format(type(data).__name__))

        return the_data

    def _load_schema(self, schema):
        the_schema = schema

        if isinstance(schema, six.string_types):
            registry = dict([(v['id'], v)
                             for v in datapackage_registry.get()])
            if schema in registry:
                the_schema = registry[schema]['schema']

        return Schema(the_schema)

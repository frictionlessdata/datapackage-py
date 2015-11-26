from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import six
import datapackage_registry
from .schema import Schema
from .resource import Resource
from .exceptions import (
    DataPackageException
)


class DataPackage(object):
    def __init__(self, metadata=None, schema='base', default_base_path=None):
        self._metadata = self._load_metadata(metadata)
        self._schema = self._load_schema(schema)
        self._base_path = self._get_base_path(metadata, default_base_path)
        self._resources = self._load_resources(self.metadata, self.base_path)

    @property
    def metadata(self):
        return self._metadata

    @property
    def schema(self):
        return self._schema

    @property
    def base_path(self):
        return self.metadata.get('base', self._base_path)

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
        return self._metadata

    def validate(self):
        self.schema.validate(self.to_dict())

    def _load_metadata(self, metadata):
        the_metadata = metadata

        if the_metadata is None:
            the_metadata = {}

        if isinstance(the_metadata, six.string_types):
            try:
                the_metadata = json.load(open(metadata, 'r'))
            except (ValueError, IOError) as e:
                msg = 'Unable to load JSON at \'{0}\''.format(metadata)
                six.raise_from(DataPackageException(msg), e)
        if not isinstance(the_metadata, dict):
            msg = 'Data must be a \'dict\', but was a \'{0}\''
            raise DataPackageException(msg.format(type(metadata).__name__))

        return the_metadata

    def _load_schema(self, schema):
        the_schema = schema

        if isinstance(schema, six.string_types):
            registry = dict([(v['id'], v)
                             for v in datapackage_registry.get()])
            if schema in registry:
                the_schema = registry[schema]['schema']

        return Schema(the_schema)

    def _get_base_path(self, metadata, default_base_path):
        try:
            return metadata['base']
        except (TypeError, KeyError):
            pass

        try:
            return os.path.dirname(os.path.abspath(metadata))
        except AttributeError:
            return default_base_path

    def _load_resources(self, metadata, base_path):
        resources_dicts = metadata.get('resources')

        if resources_dicts is None:
            return ()

        return tuple([Resource.load(resource_dict, base_path)
                      for resource_dict in resources_dicts])

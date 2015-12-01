from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
import copy
import six
import requests
import datapackage_registry
from datapackage_registry.exceptions import DataPackageRegistryException
from .schema import Schema
from .resource import Resource
from .exceptions import (
    DataPackageException,
    SchemaError
)


class DataPackage(object):
    '''Class for loading, validating and working with a Data Package.

    Args:
        metadata (dict or str, optional): The contents of the
            `datapackage.json` file. It can be a ``dict`` with its contents,
            the local path for the file or its URL. If you're passing a
            ``dict``, it's a good practice to also set the
            ``default_base_path`` parameter to the absolute `datapackage.json`
            path.
        schema (dict or str, optional): The schema to be used to validate this
            data package. If can be a ``dict`` with the schema's contents or a
            ``str``. The string can contain the schema's ID if it's in the
            registry, a local path, or an URL.
        default_base_path (str, optional): The default path to be used to load
            resources located on the local disk that don't define a base path
            themselves. This will usually be the path for the
            `datapackage.json` file. If the :data:`metadata` parameter was the
            path to the `datapackage.json`, this will automatically be set to
            its base path.

    Raises:
        DataPackageException: If the :data:`metadata` couldn't be loaded or was
            invalid.
        SchemaError: If the :data:`schema` couldn't be loaded or was invalid.
        ResourceError: If any resource defined in :data:`metadata` couldn't be
            loaded.
    '''

    def __init__(self, metadata=None, schema='base', default_base_path=None):
        self._metadata = self._load_metadata(metadata)
        self._schema = self._load_schema(schema)
        self._base_path = self._get_base_path(metadata, default_base_path)
        self._resources = self._load_resources(self.metadata, self.base_path)

    @property
    def metadata(self):
        '''dict: The metadata of this data package. Its attributes can be
        changed.'''
        return self._metadata

    @property
    def schema(self):
        ''':class:`.Schema`: The schema of this data package.'''
        return self._schema

    @property
    def base_path(self):
        '''str: The base path of this Data Package (can be None).'''
        return self.metadata.get('base', self._base_path)

    @property
    def resources(self):
        '''The resources defined in this data package (can be empty).

        To add or remove resources, alter the `resources` attribute of the
        :data:`metadata`.

        :returns: The resources.
        :rtype: tuple of :class:`.Resource`

        Raises:
            ResourceError: If any resource couldn't be loaded.
        '''
        self._resources = self._update_resources(self._resources,
                                                 self.metadata,
                                                 self.base_path)
        return self._resources

    @property
    def attributes(self):
        '''tuple: The union of the attributes defined in the schema and the
        data package (can be empty).'''
        attributes = set(self.to_dict().keys())
        try:
            attributes.update(self.schema.properties.keys())
        except AttributeError:
            pass
        return tuple(attributes)

    @property
    def required_attributes(self):
        '''tuple: The schema's required attributed (can be empty).'''
        required = ()
        try:
            if self.schema.required is not None:
                required = tuple(self.schema.required)
        except AttributeError:
            pass
        return required

    def to_dict(self):
        '''dict: Convert this Data Package to dict.'''
        return copy.deepcopy(self.metadata)

    def validate(self):
        '''Validate this Data Package.

        Raises:
            DataPackageValidateException: If the Data Package is invalid.
        '''
        self.schema.validate(self.to_dict())

    def _load_metadata(self, metadata):
        the_metadata = metadata

        if the_metadata is None:
            the_metadata = {}

        if isinstance(the_metadata, six.string_types):
            try:
                if os.path.isfile(the_metadata):
                    with open(the_metadata, 'r') as f:
                        the_metadata = json.load(f)
                else:
                    req = requests.get(the_metadata)
                    req.raise_for_status()
                    the_metadata = req.json()
            except (IOError,
                    ValueError,
                    requests.exceptions.RequestException) as e:
                msg = 'Unable to load JSON at \'{0}\''.format(metadata)
                six.raise_from(DataPackageException(msg), e)

        if not isinstance(the_metadata, dict):
            msg = 'Data must be a \'dict\', but was a \'{0}\''
            raise DataPackageException(msg.format(type(metadata).__name__))

        return the_metadata

    def _load_schema(self, schema):
        the_schema = schema

        if isinstance(schema, six.string_types):
            try:
                registry = datapackage_registry.Registry()
                registry_schema = registry.get(schema)
                if registry_schema is not None:
                    the_schema = registry_schema
            except DataPackageRegistryException as e:
                six.raise_from(SchemaError(e), e)

        return Schema(the_schema)

    def _get_base_path(self, metadata, default_base_path):
        base_path = default_base_path

        if isinstance(metadata, dict) and 'base' in metadata:
            base_path = metadata['base']
        elif isinstance(metadata, six.string_types):
            if os.path.exists(metadata):
                base_path = os.path.dirname(os.path.abspath(metadata))
            else:
                # suppose metadata is a URL
                base_path = os.path.dirname(metadata)

        return base_path

    def _load_resources(self, metadata, base_path):
        return self._update_resources((), metadata, base_path)

    def _update_resources(self, current_resources, metadata, base_path):
        resources_dicts = metadata.get('resources')
        new_resources = []

        if resources_dicts is not None:
            for resource_dict in resources_dicts:
                resource = [res for res in current_resources
                            if res.metadata == resource_dict]
                if not resource:
                    resource = [Resource.load(resource_dict, base_path)]
                new_resources.append(resource[0])

        return tuple(new_resources)

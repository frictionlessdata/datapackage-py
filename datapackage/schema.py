from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import copy
import six
import requests
import json
import jsonschema
import datapackage.registry
from .exceptions import (
    SchemaError,
    ValidationError,
)


class Schema(object):
    '''Abstracts a JSON Schema and allows validation of data against it.

    Args:
        schema (str or dict): The JSON Schema itself as a dict, a local path
            or URL to it.

    Raises:
        SchemaError: If unable to load schema or it was invalid.
        RegistryError: If there was some error loading the schema registry.

    Warning:
        The schema objects created with this class are read-only. You should
        change any of its attributes after creation.
    '''
    def __init__(self, schema):
        self._registry = self._load_registry()
        self._schema = self._load_schema(schema, self._registry)
        self._validator = self._load_validator(self._schema, self._registry)
        self._check_schema()

    def to_dict(self):
        '''dict: Convert this :class:`.Schema` to dict.'''
        return copy.deepcopy(self._schema)

    def validate(self, data):
        '''Validates a data dict against this schema.

        Args:
            data (dict): The data to be validated.

        Raises:
            ValidationError: If the data is invalid.
        '''
        try:
            self._validator.validate(data)
        except jsonschema.ValidationError as e:
            six.raise_from(ValidationError.create_from(e), e)

    def iter_errors(self, data):
        '''Lazily yields each ValidationError for the received data dict.

        Args:
            data (dict): The data to be validated.

        Returns:
            iter: ValidationError for each error in the data.
        '''
        for error in self._validator.iter_errors(data):
            yield ValidationError.create_from(error)

    def _load_registry(self):
        return datapackage.registry.Registry()

    def _load_schema(self, schema, registry):
        the_schema = schema

        if isinstance(schema, six.string_types):
            try:
                the_schema = registry.get(schema)
                if not the_schema:
                    if os.path.isfile(schema):
                        with open(schema, 'r') as f:
                            the_schema = json.load(f)
                    else:
                        req = requests.get(schema)
                        req.raise_for_status()
                        the_schema = req.json()
            except (IOError,
                    ValueError,
                    requests.exceptions.RequestException) as e:
                msg = 'Unable to load schema at "{0}"'
                six.raise_from(SchemaError(msg.format(schema)), e)
        elif isinstance(the_schema, dict):
            the_schema = copy.deepcopy(the_schema)
        else:
            msg = 'Schema must be a "dict", but was a "{0}"'
            raise SchemaError(msg.format(type(the_schema).__name__))

        return the_schema

    def _load_validator(self, schema, registry):
        resolver = None

        if registry.base_path:
            path = 'file://{base_path}/'.format(base_path=registry.base_path)
            resolver = jsonschema.RefResolver(path, schema)

        validator_class = jsonschema.validators.validator_for(schema)

        return validator_class(schema, resolver=resolver)

    def _check_schema(self):
        try:
            self._validator.check_schema(self._schema)
        except jsonschema.exceptions.SchemaError as e:
            six.raise_from(SchemaError.create_from(e), e)

    def __getattr__(self, name):
        if name in self.__dict__.get('_schema', {}):
            return copy.deepcopy(self._schema[name])

        msg = '\'{0}\' object has no attribute \'{1}\''
        raise AttributeError(msg.format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self.__dict__.get('_schema', {}):
            raise AttributeError('can\'t set attribute')
        super(self.__class__, self).__setattr__(name, value)

    def __dir__(self):
        return list(self.__dict__.keys()) + list(self._schema.keys())

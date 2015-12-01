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
import datapackage_validate
from datapackage_validate.exceptions import DataPackageValidateException
from .exceptions import (
    SchemaError, ValidationError
)


class Schema(object):
    '''Abstracts a JSON Schema and allows validation of data against it.

    Args:
        schema (str or dict): The JSON Schema itself as a dict, or a local path
            or URL to it.

    Raises:
        SchemaError: If unable to load schema or it was invalid.

    Warning:
        The schema objects created with this class are read-only. You should
        change any of its attributes after creation.
    '''
    def __init__(self, schema):
        self._schema = self._load_schema(schema)
        validator_class = jsonschema.validators.validator_for(self._schema)
        self._validator = validator_class(self._schema)
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
            datapackage_validate.validate(data, self.to_dict())
        except DataPackageValidateException as e:
            six.raise_from(ValidationError(e), e)

    def _load_schema(self, schema):
        the_schema = schema

        if isinstance(schema, six.string_types):
            try:
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
                msg = 'Unable to load JSON at "{0}"'
                six.raise_from(SchemaError(msg.format(schema)), e)
        elif isinstance(the_schema, dict):
            the_schema = copy.deepcopy(the_schema)
        else:
            msg = 'Schema must be a "dict", but was a "{0}"'
            raise SchemaError(msg.format(type(the_schema).__name__))

        return the_schema

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

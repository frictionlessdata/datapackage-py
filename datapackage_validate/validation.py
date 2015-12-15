from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import jsonschema
import datapackage_registry
from datapackage_registry.exceptions import DataPackageRegistryException

from . import compat
from .exceptions import (
    DataPackageValidateException,
    SchemaError,
    ValidationError,
    RegistryError,
)


def validate(datapackage, schema='base'):
    '''Validate Data Package datapackage.json files against a jsonschema.

    `datapackage` - a json string or python dict
    `schema` - a schema string id, json string, or python dict

    Returns None.

    Raises a `datapackage_validate.exceptions.DataPackageValidateException`
    with a list of the validation errors in its `.errors` attribute.
    '''

    errors = []
    schema_obj = None
    datapackage_obj = None
    registry = None

    # Sanity check datapackage
    # If datapackage is a str, check json is well formed
    if isinstance(datapackage, compat.str):
        try:
            datapackage_obj = json.loads(datapackage)
        except ValueError as e:
            errors.append(DataPackageValidateException(e))
    elif not (isinstance(datapackage, dict) or isinstance(datapackage, list)):
        msg = 'Data Package must be a dict or JSON string, but was a \'{0}\''
        dp_type = type(datapackage).__name__
        error = DataPackageValidateException(msg.format(dp_type))
        errors.append(error)
    else:
        datapackage_obj = datapackage

    # Sanity check schema (and get from registry if necessary)
    # If the schema is a string...
    if isinstance(schema, compat.str):
        # Try to load schema as a json string
        try:
            schema_obj = json.loads(schema)
        except ValueError as e:
            # Can't load as json, assume string is a schema id
            # Get schema from registry
            try:
                registry = datapackage_registry.Registry()
                schema_obj = registry.get(schema)
                if schema_obj is None:
                    msg = 'No schema with id \'{0}\''.format(e)
                    errors.append(RegistryError(msg))
            except DataPackageRegistryException as e:
                errors.append(RegistryError(e))
    elif not isinstance(schema, dict):
        msg = 'Schema must be a string or dict'
        errors.append(SchemaError(msg))
    else:
        schema_obj = schema

    # Validate datapackage against the schema
    if datapackage_obj is not None and schema_obj is not None:
        try:
            validator = _get_validator_for(schema_obj, registry)
            validator.validate(datapackage_obj)
        except jsonschema.ValidationError as e:
            errors.append(ValidationError(e.message))

    if errors:
        exception = DataPackageValidateException()
        exception.errors = errors
        raise exception


def _get_validator_for(schema, registry=None):
    resolver = None
    if registry and registry.base_path is not None:
        path = 'file://{base_path}/'.format(base_path=registry.base_path)
        resolver = jsonschema.RefResolver(path, schema)

    validator = jsonschema.validators.validator_for(schema)
    return validator(schema, resolver=resolver)

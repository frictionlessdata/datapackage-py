from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import jsonschema
import datapackage_registry
import requests

from . import compat
from . import exceptions


def _get_schema_url_from_registry(id, registry):
    '''Return schema url corresponding with `id` from `registry`, or None'''
    return next((s['schema'] for s in registry if s['id'] == id), None)


def _fetch_schema_obj_from_url(url):
    '''Fetch schema from url and return schema dict'''
    schema_response = requests.get(url)
    schema_response.raise_for_status()
    return json.loads(schema_response.text)


def validate(datapackage, schema='base'):
    '''Validate Data Package datapackage.json files against a jsonschema.

    `datapackage` - a json string or python dict
    `schema` - a schema string id, json string, or python dict

    Return a tuple (valid, errors):

    `valid` - a boolean to determine whether the datapackage validates against
    the schema.
    `errors` - a list of exceptions found during validation. Empty if `valid`
    is True.
    '''

    valid = False
    errors = []
    schema_obj = None
    datapackage_obj = None

    # Sanity check datapackage
    # If datapackage is a str, check json is well formed
    if isinstance(datapackage, compat.str):
        try:
            datapackage_obj = json.loads(datapackage)
        except ValueError as e:
            errors.append(exceptions.DataPackageValidateException(e))
    elif not (isinstance(datapackage, dict) or isinstance(datapackage, list)):
        msg = 'Data Package must be a dict or JSON string, but was a \'{0}\''
        dp_type = type(datapackage).__name__
        error = exceptions.DataPackageValidateException(msg.format(dp_type))
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
                registry = datapackage_registry.get()
            except requests.HTTPError as e:
                errors.append(exceptions.RegistryError(e))
            else:
                schema_url = _get_schema_url_from_registry(schema, registry)
                if schema_url is None:
                    msg = 'No schema with id \'{0}\''.format(e)
                    errors.append(exceptions.RegistryError(msg))
                else:
                    try:
                        schema_obj = _fetch_schema_obj_from_url(schema_url)
                    except requests.HTTPError as e:
                        errors.append(exceptions.RegistryError(e))
    elif not isinstance(schema, dict):
        msg = 'Schema must be a string or dict'
        errors.append(exceptions.SchemaError(msg))
    else:
        schema_obj = schema

    # Validate datapackage against the schema
    if datapackage_obj and schema_obj:
        try:
            jsonschema.validate(datapackage_obj, schema_obj)
        except jsonschema.ValidationError as e:
            errors.append(exceptions.ValidationError(e.message))
        else:
            valid = True

    return valid, errors

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import jsonschema
import datapackage_registry
import requests

from . import compat


def _get_schema_url_from_registry(id, registry):
    '''Return schema url corresponding with `id` from `registry`, or None'''
    return next((s['schema'] for s in registry if s['id'] == id), None)


def _fetch_schema_obj_from_url(url):
    '''Fetch schema from url and return schema object'''
    # ::TODO:: handle HTTPError when fetching schema from url
    schema_response = requests.get(url)
    return json.loads(schema_response.text)


def validate(datapackage, schema='base'):
    '''
    `datapackage` is a json string or python object

    `schema` is a schema string id, json string, or python dict
    '''

    valid = False
    errors = []
    schema_obj = None

    # Sanity check datapackage
    # If datapackage is a str, check json is well formed
    if isinstance(datapackage, compat.str):
        try:
            datapackage_obj = json.loads(datapackage)
        except ValueError as e:
            datapackage_obj = None
            errors.append('Invalid JSON: {0}'.format(e))
    elif not (isinstance(datapackage, dict) or isinstance(datapackage, list)):
        datapackage_obj = None
        errors.append('Invalid Data Package: not a string or object')
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
            registry = datapackage_registry.get()
            schema_url = _get_schema_url_from_registry(schema, registry)

            if schema_url is None:
                errors.append(
                    'Registry Error: no schema with id "{0}"'.format(schema))
            else:
                schema_obj = _fetch_schema_obj_from_url(schema_url)
    elif not isinstance(schema, dict):
        schema_obj = None
        errors.append('Invalid Schema: not a string or object')
    else:
        schema_obj = schema

    # Validate datapackage against the schema
    if datapackage_obj and schema_obj:
        try:
            jsonschema.validate(datapackage_obj, schema_obj)
        except jsonschema.ValidationError as e:
            errors.append('Schema ValidationError: {0}'.format(e.message))
        else:
            valid = True

    return valid, errors

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

import jsonschema
import datapackage_registry
import requests


# from . import compat


def _get_schema_url_from_registry(id, registry):
    '''Return schema url corresponding with `id` from `registry`, or None'''
    return next((s['schema'] for s in registry if s['id'] == id), None)


def _fetch_schema_obj_from_url(url):
    '''Fetch schema from url and return schema object'''
    # ::TODO:: handle HTTPError when fetching schema from url
    schema_response = requests.get(url)
    return json.loads(schema_response.text)


def validate(datapackage, schema=None):
    '''
    `datapackage` is a json string or python object

    `schema` is a schema string id, json string, or python dict
    '''
    schema = schema or 'base'

    # ::TODO:: probably don't want to set valid to True here. Default to
    # False, then set to true if jsonschema.validate doesn't raise exceptions
    valid = True
    errors = []
    schema_obj = None

    # check json is well formed
    if type(datapackage) is unicode:
        try:
            json.loads(datapackage)
        except ValueError as e:
            valid = False
            errors.append('Invalid JSON: {0}'.format(e))
            return valid, errors
    # ::TODO:: what if datapackage is already a python object?

    # If the schema is a string...
    if type(schema) is unicode:
        # Try to load schema as a json string
        try:
            schema_obj = json.loads(schema)
        except ValueError as e:
            # Can't load as json, assume string is a schema id
            # Get schema from registry
            registry = datapackage_registry.get()
            schema_url = _get_schema_url_from_registry(schema, registry)

            if schema_url is None:
                valid = False
                errors.append(
                    'Registry Error: no schema with id "{0}"'.format(schema))
                # ::TODO:: refactor to remove this premature return
                return valid, errors

            schema_obj = _fetch_schema_obj_from_url(schema_url)

    # If schema is a dict, assume it's a schema object
    elif type(schema) is dict:
        schema_obj = schema

    if schema_obj:
        try:
            jsonschema.validate(json.loads(datapackage), schema_obj)
        except jsonschema.ValidationError as e:
            valid = False
            errors.append('Schema ValidationError: {0}'.format(e.message))
    # ::TODO:: errors for no schema_obj

    return valid, errors

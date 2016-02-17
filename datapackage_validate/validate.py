from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import six

from .schema import Schema

from .exceptions import (
    DataPackageValidateException,
    SchemaError,
    ValidationError,
    RegistryError,
)


def validate(datapackage, schema='base'):
    '''Validate Data Package datapackage.json files against a jsonschema.

    Args:
        datapackage (str or dict): The Data Package descriptor file (i.e.
            datapackage.json) as a dict or its contents in a string.
        schema (str or dict): If a string, it can be the schema ID in the
            registry, a local path, a URL or the schema's JSON as a string. If
            a dict, it must be the JSON Schema itself.

    Returns:
        None

    Raises:
        DataPackageValidateException: This exception has the list of the
            validation errors in its `.errors` attribute.
    '''

    errors = []
    schema_obj = None
    datapackage_obj = None

    # Sanity check datapackage
    # If datapackage is a str, check json is well formed
    if isinstance(datapackage, six.string_types):
        try:
            datapackage_obj = json.loads(datapackage)
        except ValueError as e:
            errors.append(DataPackageValidateException(e))
    elif not isinstance(datapackage, dict):
        msg = 'Data Package must be a dict or JSON string, but was a \'{0}\''
        dp_type = type(datapackage).__name__
        error = DataPackageValidateException(msg.format(dp_type))
        errors.append(error)
    else:
        datapackage_obj = datapackage

    try:
        if isinstance(schema, six.string_types):
            try:
                schema = json.loads(schema)
            except ValueError:
                pass

        schema_obj = Schema(schema)
    except (SchemaError,
            RegistryError) as e:
        errors.append(e)

    # Validate datapackage against the schema
    if datapackage_obj is not None and schema_obj is not None:
        try:
            schema_obj.validate(datapackage_obj)
        except ValidationError as e:
            errors.append(e)

    if errors:
        exception = DataPackageValidateException()
        exception.errors = errors
        raise exception

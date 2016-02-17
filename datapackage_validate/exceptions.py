from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema.exceptions


class DataPackageValidateException(Exception):
    pass


class SchemaError(DataPackageValidateException,
                  jsonschema.exceptions.SchemaError):
    pass


class ValidationError(DataPackageValidateException,
                      jsonschema.exceptions.ValidationError):
    pass


class RegistryError(DataPackageValidateException):
    pass

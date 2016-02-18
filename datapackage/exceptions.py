from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema.exceptions


class DataPackageException(Exception):
    pass


class SchemaError(DataPackageException,
                  jsonschema.exceptions.SchemaError):
    pass


class ValidationError(DataPackageException,
                      jsonschema.exceptions.ValidationError):
    pass


class RegistryError(DataPackageException):
    pass

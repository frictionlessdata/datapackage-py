from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema.exceptions


# Module API

class DataPackageException(Exception):

    # Public

    def __init__(self, message, errors=[]):
        self.__errors = errors
        super(Exception, self).__init__(message)

    @property
    def multiple(self):
        return bool(self.__errors)

    @property
    def errors(self):
        return self.__errors


class ValidationError(DataPackageException, jsonschema.exceptions.ValidationError):
    pass


# Deprecated

class SchemaError(DataPackageException, jsonschema.exceptions.SchemaError):
    pass

class RegistryError(DataPackageException):
    pass

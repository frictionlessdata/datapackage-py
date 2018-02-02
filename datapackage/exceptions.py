'''Exceptions thrown by the datapackage library.

All exceptions inherit from `DataPackageException`, so you can use it as a
catch-all. Some exceptions contain multiple errors, for example to get the list
of a data package's validation errors. If that's the case, the errors will be
in the `exception.errors` list.
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tableschema


# Module API

DataPackageException = tableschema.exceptions.DataPackageException
TableSchemaException = tableschema.exceptions.TableSchemaException
LoadError = tableschema.exceptions.LoadError
ValidationError = tableschema.exceptions.ValidationError
CastError = tableschema.exceptions.CastError
RelationError = tableschema.exceptions.RelationError
StorageError = tableschema.exceptions.StorageError


# Deprecated

class SchemaError(DataPackageException):
    pass


class RegistryError(DataPackageException):
    pass

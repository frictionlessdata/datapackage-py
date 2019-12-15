from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tableschema


# Module API

DataPackageException = tableschema.DataPackageException
TableSchemaException = tableschema.TableSchemaException
LoadError = tableschema.LoadError
ValidationError = tableschema.ValidationError
CastError = tableschema.CastError
IntegrityError = tableschema.IntegrityError
RelationError = tableschema.RelationError
StorageError = tableschema.StorageError


# Deprecated

class SchemaError(DataPackageException):
    pass


class RegistryError(DataPackageException):
    pass

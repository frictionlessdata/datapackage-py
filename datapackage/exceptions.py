from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datapackage_validate.exceptions


class DataPackageException(Exception):
    pass


SchemaError = datapackage_validate.exceptions.SchemaError
ValidationError = datapackage_validate.exceptions.ValidationError

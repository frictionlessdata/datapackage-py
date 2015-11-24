class DataPackageValidateException(Exception):
    pass


class SchemaError(DataPackageValidateException):
    pass


class ValidationError(DataPackageValidateException):
    pass


class RegistryError(DataPackageValidateException):
    pass

class DataPackageValidateException(Exception):
    def __init__(self, *args, **kwargs):
        super(DataPackageValidateException, self).__init__(*args, **kwargs)
        self.errors = []


class SchemaError(DataPackageValidateException):
    pass


class ValidationError(DataPackageValidateException):
    pass


class RegistryError(DataPackageValidateException):
    pass

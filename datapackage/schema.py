import six
import json
import jsonschema


SchemaError = jsonschema.exceptions.SchemaError
ValidationError = jsonschema.exceptions.ValidationError


class Schema(object):
    def __init__(self, schema):
        self.__schema = self.__load_schema(schema)
        validator_class = jsonschema.validators.validator_for(self.schema)
        self.__validator = validator_class(self.schema)
        self.__validator.check_schema(self.schema)

    @property
    def schema(self):
        return self.__schema

    def validate(self, data):
        self.__validator.validate(data)

    def __load_schema(self, schema):
        the_schema = schema
        if isinstance(schema, six.string_types):
            the_schema = json.load(open(schema, 'r'))
        if not isinstance(the_schema, dict):
            msg = 'Schema must be a "dict", but was a "{0}"'
            raise SchemaError(msg.format(type(the_schema).__name__))
        return the_schema

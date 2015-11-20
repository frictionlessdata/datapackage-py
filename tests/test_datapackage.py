import pytest
import datapackage


class TestDataPackage(object):
    def test_schema(self):
        descriptor = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(descriptor, schema=schema)
        assert dp.schema.to_dict() == schema

    def test_datapackage_attributes(self):
        dp = datapackage.DataPackage()
        dp.foo = 'bar'
        dp.bar = 'baz'
        assert dp.attributes == {'foo': 'bar', 'bar': 'baz'}

    def test_validate(self):
        descriptor = {
            'name': 'foo',
        }
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(descriptor, schema)
        dp.validate()

    def test_validate_raises_validation_error_if_invalid(self):
        schema = {
            'properties': {
                'name': {},
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(schema=schema)
        with pytest.raises(datapackage.exceptions.ValidationError):
            dp.validate()

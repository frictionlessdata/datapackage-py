import pytest
import datapackage


class TestDataPackage(object):
    def test_init_uses_base_schema_by_default(self):
        dp = datapackage.DataPackage()
        assert dp.schema.title == 'DataPackage'

    def test_schema(self):
        descriptor = {}
        schema = {'foo': 'bar'}
        dp = datapackage.DataPackage(descriptor, schema=schema)
        assert dp.schema.to_dict() == schema

    def test_attributes(self):
        descriptor = {
            'name': 'foo',
        }
        dp = datapackage.DataPackage(descriptor)
        dp.title = 'bar'
        assert dp.attributes == {'name': 'foo', 'title': 'bar'}

    def test_attributes_arent_immutable(self):
        descriptor = {
            'keywords': [],
        }
        dp = datapackage.DataPackage(descriptor)
        dp.keywords.append('foo')
        assert dp.attributes == {'keywords': ['foo']}

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

    def test_validate_works_when_setting_attributes_after_creation(self):
        schema = {
            'properties': {
                'name': {}
            },
            'required': ['name'],
        }
        dp = datapackage.DataPackage(schema=schema)
        dp.name = 'foo'
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

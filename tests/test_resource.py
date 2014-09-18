import datapackage
import posixpath
from nose.tools import raises
from mock import Mock, patch
import sys

if sys.version_info[0] < 3:
    next = lambda x: x.next()
    bytes = str
    str = unicode


class TestDatapackage(object):
    def setup(self):
        self.dpkg = datapackage.DataPackage("tests/test.dpkg")
        kwargs = self.dpkg['resources'][0]
        kwargs['datapackage_uri'] = str(self.dpkg.base)
        self.resource = datapackage.Resource(**kwargs)

    def teardown(self):
        pass

    def patch_urlopen_size(self, mock_urlopen, size):
        mock_meta = Mock()
        mock_meta.getheaders.side_effect = [[size]]

        mock_site = Mock()
        mock_site.info.return_value = mock_meta

        mock_urlopen.return_value = mock_site

    def test_get_data(self):
        """Try reading the resource data"""
        data = self.resource.data
        assert data == {"foo": "bar"}

    def test_get_missing_data(self):
        """Try reading missing resource data"""
        del self.resource['data']
        data = self.resource.data
        assert data is None

    def test_clear_data(self):
        """Check that setting data to none removes it from the descriptor"""
        self.resource.data = None
        assert 'data' not in self.resource

    def test_set_data(self):
        """Check that setting the data works"""
        # 1 will get converted to "1" because it gets translated into
        # a json object, and json keys are always strings
        self.resource.data = {"foo": "bar", 1: 2}
        assert "foo" in self.resource.data
        assert self.resource.data["foo"] == "bar"
        assert 1 in self.resource.data, self.resource.data
        assert self.resource.data[1] == 2

    def test_get_path(self):
        """Try reading the resource path"""
        path = self.resource.path
        assert path == "foobar.json"

    def test_get_fullpath(self):
        """Try reading the full resource path"""
        path = self.resource.fullpath
        assert path == posixpath.join(self.dpkg.base, "foobar.json"),\
            path
        assert posixpath.exists(path)

    def test_get_missing_path(self):
        """Try reading the path when it is missing"""
        del self.resource['path']
        path = self.resource.path
        assert path is None

    def test_get_missing_fullpath(self):
        """Try reading the full path when it is missing"""
        del self.resource['path']
        path = self.resource.fullpath
        assert path is None

    def test_clear_path(self):
        """Check that setting path to none removes it from the descriptor"""
        self.resource.path = None
        assert 'path' not in self.resource

    def test_set_path(self):
        """Check that setting the path works"""
        self.resource.path = str("barfoo.json")
        assert self.resource.path == "barfoo.json"
        assert self.resource.fullpath == posixpath.join(self.dpkg.base,
                                                        "barfoo.json")

    def test_get_url(self):
        """Try reading the resource url"""
        url = self.resource.url
        assert url == "http://foobar.com/foobar.json"

    def test_get_missing_url(self):
        """Try reading the resource url when it is missing"""
        del self.resource['url']
        url = self.resource.url
        assert url is None

    def test_clear_url(self):
        """Check that setting the url to none removes it from the descriptor"""
        self.resource.url = None
        assert 'url' not in self.resource

    def test_set_url(self):
        """Try setting the resource url"""
        self.resource.url = str("https://www.google.com")
        assert self.resource.url == "https://www.google.com",\
            self.resource.url

    @raises(ValueError)
    def test_set_bad_url(self):
        """Try setting the resource url to an invalid url"""
        self.resource.url = str("google")

    def test_get_name(self):
        """Try reading the resource name"""
        assert self.resource.name == "foobar"

    def test_get_default_name(self):
        """Try reading the default resource name"""
        del self.resource['name']
        assert self.resource.name == str('')

    def test_set_name(self):
        """Try setting the resource name"""
        self.resource.name = str("barfoo")
        assert self.resource.name == "barfoo"

    def test_set_name_to_none(self):
        """Try setting the resource name to none"""
        self.resource.name = None
        assert self.resource.name == '', self.resource.name

    @raises(ValueError)
    def test_set_invalid_name(self):
        """Try setting the resource name to an invalid name"""
        self.resource.name = str("foo bar")

    def test_get_format(self):
        """Try reading the resource format"""
        assert self.resource.format == str("json")

    def test_get_default_format(self):
        """Try reading the default resource format"""
        del self.resource['format']
        assert self.resource.format == ''

    def test_set_format(self):
        """Try setting the resource format"""
        self.resource.format = str('csv')
        assert self.resource.format == 'csv'

    def test_set_format_to_none(self):
        """Try setting the resource format to none"""
        self.resource.format = None
        assert self.resource.format == ''
        assert self.resource['format'] == ''

    def test_get_mediatype(self):
        """Try reading the resource mediatype"""
        assert self.resource.mediatype == "application/json"

    def test_get_default_mediatype(self):
        """Try reading the default mediatype"""
        del self.resource['mediatype']
        assert self.resource.mediatype == ''

    def test_set_mediatype(self):
        """Try setting the resource mediatype"""
        self.resource.mediatype = str('text/csv')
        assert self.resource.mediatype == 'text/csv'

    def test_set_mediatype_to_none(self):
        """Try setting the resource mediatype to none"""
        self.resource.mediatype = None
        assert self.resource.mediatype == ''
        assert self.resource['mediatype'] == ''

    @raises(ValueError)
    def test_set_invalid_mediatype(self):
        """Try setting the resource mediatype to an invalid mimetype"""
        self.resource.mediatype = str("foo")

    def test_get_encoding(self):
        """Try reading the resource encoding"""
        assert self.resource.encoding == 'utf-8'

    def test_get_default_encoding(self):
        """Try reading the default encoding"""
        del self.resource['encoding']
        assert self.resource.encoding == 'utf-8'

    def test_set_encoding(self):
        """Try setting the resource encoding"""
        self.resource.encoding = str('latin1')
        assert self.resource.encoding == 'latin1'

    def test_set_encoding_to_none(self):
        """Try setting the resource encoding to none"""
        self.resource.encoding = None
        assert self.resource.encoding == 'utf-8'
        assert self.resource['encoding'] == 'utf-8'

    def test_guess_mediatype(self):
        assert self.resource._guess_mediatype() == 'application/json'
        self.resource.path = str("foo.csv")
        assert self.resource._guess_mediatype() == 'text/csv'
        self.resource.path = str("foo.jpg")
        assert self.resource._guess_mediatype() == 'image/jpeg'

        self.resource.path = None
        assert self.resource._guess_mediatype() == 'application/json'
        self.resource.url = str("http://foobar.com/foo.csv")
        assert self.resource._guess_mediatype() == 'text/csv'
        self.resource.url = str("http://foobar.com/foo.jpg")
        assert self.resource._guess_mediatype() == 'image/jpeg'

    def test_guess_format(self):
        assert self.resource._guess_format() == 'json'
        self.resource.path = str("foo.csv")
        assert self.resource._guess_format() == 'csv'
        self.resource.path = str("foo.jpg")
        assert self.resource._guess_format() == 'jpg'

        self.resource.path = None
        self.resource.url = str("http://foobar.com/foo.json")
        assert self.resource._guess_format() == 'json'
        self.resource.url = str("http://foobar.com/foo.csv")
        assert self.resource._guess_format() == 'csv'
        self.resource.url = str("http://foobar.com/foo.jpg")
        assert self.resource._guess_format() == 'jpg'

        self.resource.url = None
        self.resource.mediatype = str("application/json")
        assert self.resource._guess_format() == 'json'
        self.resource.mediatype = str("text/csv")
        assert self.resource._guess_format() == 'csv'
        self.resource.mediatype = str("image/jpeg")
        assert self.resource._guess_format() == 'jpe'

    def test_data_bytes(self):
        """Checks that the size is computed correctly from the data"""
        assert self.resource._data_bytes() == self.resource.bytes

    @raises(ValueError)
    def test_data_bytes_no_data(self):
        """Check that an error is raised when _data_bytes is called but there
        is no data

        """
        self.resource.data = None
        self.resource._data_bytes()

    def test_path_bytes(self):
        """Checks that the size is computed correctly from the path"""
        assert self.resource._path_bytes() == self.resource.bytes

    @raises(ValueError)
    def test_path_bytes_no_path(self):
        """Check that an error is raised when _path_bytes is called but there
        is no path

        """
        self.resource.path = None
        self.resource._path_bytes()

    @patch('urllib.urlopen')
    def test_url_bytes(self, mock_urlopen):
        """Checks that the size is computed correctly from the url"""
        self.patch_urlopen_size(mock_urlopen, '14')
        assert self.resource._url_bytes() == self.resource.bytes

    @raises(ValueError)
    def test_url_bytes_no_url(self):
        """Check that an error is raised when _url_bytes is called but there
        is no url

        """
        self.resource.url = None
        self.resource._url_bytes()

    def test_compute_bytes_from_data(self):
        """Test computing the size from inline data"""
        del self.resource['bytes']
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    def test_update_bytes_data_unchanged(self):
        """Test that updating the size from inline data does not throw an
        error when the size has not changed.

        """
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    def test_compute_bytes_from_path(self):
        """Test computing the size from the file given by the path"""
        self.resource.data = None
        del self.resource['bytes']
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    def test_update_bytes_path_unchanged(self):
        """Test that updating the size from the file given by the path does
        not throw an error when the size has not changed.

        """
        self.resource.data = None
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    @patch('urllib.urlopen')
    def test_compute_bytes_from_url(self, mock_urlopen):
        """Test computing the size from the url"""
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.path = None
        del self.resource['bytes']
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    @patch('urllib.urlopen')
    def test_update_bytes_url_unchanged(self, mock_urlopen):
        """Test that updating the size from the url does not throw an
        error when the size has not changed.

        """
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.path = None
        self.resource.update_bytes()
        assert self.resource.bytes == 14

    @raises(RuntimeError)
    def test_update_bytes_data_changed(self):
        """Check that updating the bytes from the inline data throws an error
        when the size has changed.

        """
        self.resource['bytes'] = 15
        self.resource.update_bytes()

    @raises(RuntimeError)
    def test_update_bytes_path_changed(self):
        """Check that updating the bytes from the path throws an error when
        the size has changed.

        """
        self.resource.data = None
        self.resource['bytes'] = 15
        self.resource.update_bytes()

    @raises(RuntimeError)
    @patch('urllib.urlopen')
    def test_update_bytes_url_changed(self, mock_urlopen):
        """Check that updating the bytes from the url throws an error when the
        size has changed.

        """
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource.path = None
        self.resource['bytes'] = 15
        self.resource.update_bytes()

    def test_update_bytes_data_changed_unverified(self):
        """Check that updating the bytes from the inline data works, when the
        size has changed but the size is not being verified.

        """
        self.resource['bytes'] = 15
        self.resource.update_bytes(verify=False)
        assert self.resource.bytes == 14
        assert self.resource['bytes'] == 14

    def test_update_bytes_path_changed_unverified(self):
        """Check that updating the bytes from the path works, when the size
        has changed but the size is not being verified.

        """
        self.resource.data = None
        self.resource['bytes'] = 15
        self.resource.update_bytes(verify=False)
        assert self.resource.bytes == 14
        assert self.resource['bytes'] == 14

    @patch('urllib.urlopen')
    def test_update_bytes_url_changed_unverified(self, mock_urlopen):
        """Check that updating the bytes from the url works, when the size has
        changed but the size is not being verified.

        """
        self.patch_urlopen_size(mock_urlopen, '14')
        self.resource.data = None
        self.resource['bytes'] = 15
        self.resource.update_bytes(verify=False)
        assert self.resource.bytes == 14
        assert self.resource['bytes'] == 14


    def test_set_licenses(self):
        """Test setting the licenses"""
        license_type = "PDDL"
        license_url = "http://opendefinition.org/licenses/odc-pddl"
        self.resource.licenses = [
            {"type": license_type,
             "url": license_url}]
        licenses = self.resource.licenses
        assert len(licenses) == 1
        assert licenses[0]["type"] == license_type
        assert licenses[0]["url"] == license_url

    def test_add_license(self):
        """Test adding another license"""
        self.resource.add_license("PDDL")
        licenses = self.resource.licenses
        assert len(licenses) == 2
        assert licenses[0]["type"] == "CC-BY"
        ccby_url = "http://creativecommons.org/licenses/by/4.0/"
        assert licenses[0]["url"] == ccby_url
        assert licenses[1]["type"] == "PDDL"

    def test_get_missing_licenses(self):
        """Check than an empty list is return when there are no licenses"""
        del self.resource['licenses']
        assert 'licenses' not in self.resource

    def test_get_sources(self):
        """Try reading the sources"""
        sources = self.resource.sources
        assert len(sources) == 1
        assert sources[0]["name"] == "World Bank and OECD"
        assert sources[0]["web"] == \
            "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
        assert 'email' not in sources[0]

    def test_get_default_sources(self):
        """Check that the default sources are removed"""
        del self.resource['sources']
        assert 'sources' not in self.resource

    def test_set_sources(self):
        """Check that setting the sources works"""
        self.resource.sources = None
        assert 'sources' not in self.resource
        self.resource.sources = [
            {"name": str("foo"), "web": str("https://bar.com/")}]
        sources = self.resource.sources
        assert len(sources) == 1
        assert sources[0]["name"] == "foo"
        assert sources[0]["web"] == "https://bar.com/"

    def test_add_source(self):
        """Try adding a new source with add_source"""
        self.resource.add_source(str("foo"), email=str("bar@test.com"))
        sources = self.resource.sources
        assert len(sources) == 2
        assert sources[0]["name"] == "World Bank and OECD"
        assert sources[0]["web"] == \
            "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
        assert sources[1]["name"] == "foo"
        assert sources[1]["email"] == "bar@test.com"

    def test_resource_schema_valid(self):
        required = datapackage.schema.Constraints(required=True)

        title = datapackage.schema.Field(
            name=str('title'), title=str('Title of Batman movie'),
            type=str('string'), constraints=required)
        actor = datapackage.schema.Field(
            name=str('actor'), title=str('Actor portraying Batman'))
        villain = datapackage.schema.Field(
            name=str('villain'), title=str('Movie villain'))

        schema = datapackage.schema.Schema(
            fields=[title, actor, villain],
            primaryKey=[title, villain])

        reference = datapackage.schema.Reference(
            datapackage=str('http://gotham.us/datapackages'),
            resource=str('villains'),
            fields=[str('name')])
        foreign_key = datapackage.schema.ForeignKey(fields=[villain],
                                                    reference=reference)

        schema.add_foreign_key(foreign_key)

        # In the assertions we will access the schema as a dictionary because
        # that's how it should get serialized
        assert 'fields' in schema, 'Fields not found in schema'
        expected_field_order = [str('title'), str('actor'), str('villain')]
        assert [f.name for f in schema['fields']] == expected_field_order, \
            'Field order is incorrect'
        # Constraints for first field should be required == True
        assert schema['fields'][0]['constraints']['required'] == True, \
            'Required constraint changes'
        assert schema['fields'][0]['type'] == title.type, \
            'Field type changes'
        assert schema['fields'][1]['title'] == actor.title, \
            'Field title changes'

        assert 'primaryKey' in schema, 'primaryKey not found in schema'
        assert schema.primaryKey == [u'title', u'villain'], \
            'primaryKey is incorrect in schema'

        assert 'foreignKeys' in schema, 'foreignKeys not found in schema'
        assert len(schema['foreignKeys']) == 1, \
            'foreignKeys does not hold a single foreignKey'
        assert schema['foreignKeys'][0]['fields'] == [str('villain')]
        schema_reference = schema['foreignKeys'][0]['reference']
        assert schema_reference['datapackage'] == reference.datapackage, \
            'Datapackage in reference changess'
        assert schema_reference['resource'] == reference.resource, \
            'Resource in reference changes'
        assert schema_reference['fields'] == [str('name')], \
            'Fields in reference changes'

    @raises(AttributeError)
    def test_resource_schema_field_constraint_invalid_constraint(self):
        datapackage.schema.Constraints(awesome=True)

    @raises(AttributeError)
    def test_resource_schema_field_missing_name(self):
        datapackage.schema.Field(title=str('Movie villain'))

    @raises(AttributeError)
    def test_resource_schema_field_invalid_attribute(self):
        datapackage.schema.Field(
            name=str('villain'), joker=str('Movie villain'))

    @raises(AttributeError)
    def test_resource_schema_invalid_attribute(self):
        title = datapackage.schema.Field(
            name=str('title'), title=str('Title of Batman movie'))
        actor = datapackage.schema.Field(
            name=str('actor'), title=str('Actor portraying Batman'))
        villain = datapackage.schema.Field(
            name=str('villain'), title=str('Movie villain'))
        datapackage.schema.Schema(
            fields=[title, actor, villain],
            description='This dataset resource shows all the Batman movies')

    @raises(AttributeError)
    def test_resource_schema_bad_primaryKey(self):
        title = datapackage.schema.Field(
            name=str('title'), title=str('Title of Batman movie'))
        actor = datapackage.schema.Field(
            name=str('actor'), title=str('Actor portraying Batman'))
        villain = datapackage.schema.Field(
            name=str('villain'), title=str('Movie villain'))
        penguin = datapackage.schema.Field(
            name=str('penguin'), title=str('Oswald Chesterfield Cobblepot'))
        schema = datapackage.schema.Schema(
            fields=[title, actor, villain],
            primaryKey=[title, penguin])

    @raises(AttributeError)
    def test_resource_schema_foreign_key_bad_attribute(self):
        villain = datapackage.schema.Field(
            name=str('villain'), title=str('Movie villain'))
        datapackage.schema.ForeignKey(
            fields=[villain], villain='Dr. Hugo Strange')

    def test_resource_schema_foreign_key_Field_field(self):
        villain = datapackage.schema.Field(
            name=str('villain'), title=str('Movie villain'))
        foreign_key = datapackage.schema.ForeignKey(fields=villain)
        assert foreign_key['fields'] == villain.name, \
            'Foreign key could not receive a Field object'

    def test_resource_schema_foreign_key_str_field(self):
        foreign_key = datapackage.schema.ForeignKey(fields=str('villain'))
        assert foreign_key['fields'] == str('villain'), \
            'Foreign key could not receive a string field representation'


    @raises(AttributeError)
    def test_resource_schema_reference_bad_attribute(self):
        reference = datapackage.schema.Reference(
            datapackage=str('http://gotham.us/datapackages'),
            badpeople=str('villains'),
            fields=[str('name')])

    @raises(ValueError)
    def test_ressource_schema_foreign_key_field_inconsistency(self):
        reference = datapackage.schema.Reference(
            datapackage=str('http://gotham.us/datapackages'),
            resource=str('villains'),
            fields=[str('name'), str('catwoman')])
        villain = datapackage.schema.Field(
            name=str('villain'), title=str('Movie villain'))
        foreign_key = datapackage.schema.ForeignKey(fields=[villain],
                                                    reference=reference)

from nose.tools import raises
from datapackage import sources as s


class TestSources(object):

    def setup(self):
        self.descriptor = {
            "sources": [
                {
                    "name": "World Bank and OECD",
                    "web": "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
                }
            ]
        }

    def teardown(self):
        pass

    def test_get_sources(self):
        """Try reading the sources"""
        sources = s.get_sources(self.descriptor)
        assert len(sources) == 1
        assert sources[0]["name"] == "World Bank and OECD"
        assert sources[0]["web"] == "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"

    def test_get_default_sources(self):
        """Check that the default sources are correct"""
        del self.descriptor['sources']
        assert s.get_sources(self.descriptor) == []

    def test_set_sources(self):
        """Check that setting the sources works"""
        s.set_sources(self.descriptor, None)
        assert len(s.get_sources(self.descriptor)) == 0
        s.set_sources(
            self.descriptor,
            [{"name": "foo", "web": "https://bar.com/"}])
        sources = s.get_sources(self.descriptor)
        assert len(sources) == 1
        assert sources[0]["name"] == "foo"
        assert sources[0]["web"] == "https://bar.com/"

    @raises(ValueError)
    def test_set_sources_bad_keys(self):
        """Check that an error occurs when the source keys are invalid"""
        s.set_sources(self.descriptor, [{"foo": "foo", "bar": "bar"}])

    @raises(ValueError)
    def test_set_sources_missing_name(self):
        """Check that an error occurs when the source name is missing"""
        s.set_sources(self.descriptor, [{"web": "foo", "email": "bar"}])

    @raises(ValueError)
    def test_set_sources_duplicate_names(self):
        """Check that an error occurs when there are duplicate sources"""
        s.set_sources(self.descriptor, [
            {"name": "foo", "email": "bar"},
            {"name": "foo", "email": "baz"}])

    @raises(ValueError)
    def test_set_sources_bad_website(self):
        """Check that an error occurs when the web URL is invalid"""
        s.set_sources(self.descriptor, [{"name": "foo", "web": "bar"}])

    @raises(ValueError)
    def test_set_sources_bad_email(self):
        """Check that an error occurs when the email is invalid"""
        s.set_sources(self.descriptor, [{"name": "foo", "email": "bar"}])

    def test_add_source(self):
        """Try adding a new source with add_source"""
        s.add_source(self.descriptor, "foo", email="bar@test.com")
        sources = s.get_sources(self.descriptor)
        assert len(sources) == 2
        assert sources[0]["name"] == "World Bank and OECD"
        assert sources[0]["web"] == "http://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
        assert sources[1]["name"] == "foo"
        assert sources[1]["email"] == "bar@test.com"

    def test_remove_source(self):
        """Try removing a source with remove_source"""
        s.remove_source(self.descriptor, "World Bank and OECD")
        assert len(s.get_sources(self.descriptor)) == 0

    @raises(KeyError)
    def test_remove_bad_source(self):
        """Check that an error occurs when removing a non-existant source"""
        s.remove_source(self.descriptor, "foo")

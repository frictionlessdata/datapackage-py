import os
import csv
import urllib
import unittest

BASE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..'
    )
)
REGISTRY_PATH = os.path.join(BASE_PATH, 'registry.csv')


class TestRegistry(unittest.TestCase):
    def test_registry_has_the_expected_headers(self):
        expected_headers = (
            'id',
            'title',
            'schema',
            'schema_path',
            'specification',
        )

        with open(REGISTRY_PATH, 'r', newline='') as f:
            headers = next(csv.reader(f))

        self.assertEqual(sorted(headers), sorted(expected_headers))

    def test_registry_schemas_have_the_required_attributes(self):
        required_attributes = (
            'id',
            'title',
            'schema',
            'schema_path',
            'specification',
        )

        with open(REGISTRY_PATH, 'r', newline='') as f:
            registry = csv.DictReader(f)
            msg = "Schema '{0}' doesn't define required attribute '{1}'"

            for schema in registry:
                for key, value in schema.items():
                    if key in required_attributes:
                        assert value != '', msg.format(schema['id'], key)

    def test_registry_schemas_have_unique_ids(self):
        with open(REGISTRY_PATH, 'r', newline='') as f:
            registry = csv.DictReader(f)
            ids = [schema['id'] for schema in registry]

            assert len(ids) == len(set(ids)), "The schemas IDs aren't unique"

    def test_schema_paths_exist_and_are_files(self):
        with open(REGISTRY_PATH, 'r', newline='') as f:
            registry = csv.DictReader(f)

            for entry in registry:
                schema_path = entry['schema_path']
                msg = "schema_path '{0}' of schema '{1}' isn't a file"
                msg = msg.format(schema_path, entry['id'])
                path = os.path.join(BASE_PATH, schema_path)
                assert os.path.isfile(path), msg

    def test_schema_urls_exist(self):
        is_successful = lambda req: req.status >= 200 and req.status < 400
        is_redirect = lambda req: req.status >= 300 and req.status < 400

        with open(REGISTRY_PATH, 'r', newline='') as f:
            registry = csv.DictReader(f)

            for entry in registry:
                try:
                    url = entry['schema']
                    res = self._make_head_request(url)
                    msg = "Error fetching schema_url '{0}' of schema '{1}'"
                    msg = msg.format(url, entry['id'])
                    assert (is_successful(res) or is_redirect(res)), msg
                except urllib.error.URLError as e:
                    raise Exception(msg) from e

    def test_specification_urls_exist(self):
        is_successful = lambda req: req.status >= 200 and req.status < 400
        is_redirect = lambda req: req.status >= 300 and req.status < 400

        with open(REGISTRY_PATH, 'r', newline='') as f:
            registry = csv.DictReader(f)

            for entry in registry:
                try:
                    url = entry['schema']
                    res = self._make_head_request(url)
                    msg = "Error fetching specification '{0}' of schema '{1}'"
                    msg = msg.format(url, entry['id'])
                    assert (is_successful(res) or is_redirect(res)), msg
                except urllib.error.URLError as e:
                    raise Exception(msg) from e

    def _make_head_request(self, url):
        req = urllib.request.Request(url, method='HEAD')
        return urllib.request.urlopen(req)

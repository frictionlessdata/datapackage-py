import os
import glob
import json
import unittest
import jsonschema

BASE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..'
    )
)


class TestSchemas(unittest.TestCase):
    def test_json_files_must_be_valid(self):
        json_glob = os.path.join(BASE_PATH, '*.json')
        json_paths = glob.glob(json_glob)

        for json_path in json_paths:
            try:
                with open(json_path, 'r') as f:
                    json.load(f)
            except ValueError as e:
                msg = "File '{0}' isn\'t a valid JSON."
                raise ValueError(msg.format(json_path)) from e

    def test_json_files_must_be_valid_json_schemas(self):
        json_glob = os.path.join(BASE_PATH, '*.json')
        json_paths = glob.glob(json_glob)

        for json_path in json_paths:
            with open(json_path, 'r') as f:
                schema = json.load(f)
            try:
                validator_class = jsonschema.validators.validator_for(schema)
                validator = validator_class(schema)
                validator.check_schema(schema)
            except jsonschema.exceptions.SchemaError as e:
                msg = "File '{0}' isn\'t a valid JSON Schema."
                raise ValueError(msg.format(json_path)) from e

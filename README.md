[![Build Status](https://travis-ci.org/okfn/datapackage-validate-py.svg)](https://travis-ci.org/okfn/datapackage-validate-py) [![Coverage Status](https://coveralls.io/repos/okfn/datapackage-validate-py/badge.svg?branch=master&service=github)](https://coveralls.io/github/okfn/datapackage-validate-py?branch=master)

# datapackage-validate-py

Validate [Data Package][] datapackage.json files against a jsonschema.

[Data Package]: http://data.okfn.org/doc/data-package

## Usage

```python
import datapackage_validate

valid, errors = datapackage_validate.validate(datapackage, schema)
```

The `datapackage` can be a json string or python object.

The `schema` can be a json string, python object, or a schema id corresponding with a schema from the registry of [Data Package Profiles][]. `schema` is optional, and will default to the `base` schema id if not provided.

`validate()` returns a tuple (valid, errors):

`valid` is a boolean determining whether the datapackage validates against the schema.

`errors` is a list of exceptions found during validation. Empty if `valid` is True.

[Data Package Profiles]: https://github.com/dataprotocols/registry

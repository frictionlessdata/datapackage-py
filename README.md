[![Build Status](https://travis-ci.org/okfn/datapackage-registry-py.svg)](https://travis-ci.org/okfn/datapackage-registry-py) [![Coverage Status](https://coveralls.io/repos/okfn/datapackage-registry-py/badge.svg?branch=master&service=github)](https://coveralls.io/github/okfn/datapackage-registry-py?branch=master)

# datapackage-registry-py
A Python library for working with a Data Package Registry.

Currently, the default registry backend is currently located at:
https://rawgit.com/dataprotocols/registry/master/registry.csv


## Usage

```python
import datapackage_registry

# get the default registry objects
registry = datapackage_registry.get()

# or pass in a config object to define a non-default backend endpoint
custom_config = {
  'backend': 'https://mycustomconfig.com/registry.csv',
}
custom_registry = datapackage_registry.get(custom_config)

# registry now has a dict with each profile, mapped by the profile's id, e.g.:
{
    'base': {
        'id': 'base',
        'schema': 'https://rawgit.com/dataprotocols/schemas/master/data-package.json',
        'specification': 'http://dataprotocols.org/data-packages',
        'title': 'Data Package'
    },
    'tabular': {
        'id': 'tabular',
        'schema': 'https://rawgit.com/dataprotocols/schemas/master/tabular-data-package.json',
        'specification': 'http://dataprotocols.org/tabular-data-package/',
        'title': 'Tabular Data Package'
   }
}
```

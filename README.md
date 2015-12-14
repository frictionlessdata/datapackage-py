[![Build Status](https://travis-ci.org/okfn/datapackage-registry-py.svg)](https://travis-ci.org/okfn/datapackage-registry-py)
[![Coverage Status](https://coveralls.io/repos/okfn/datapackage-registry-py/badge.svg?branch=master&service=github)](https://coveralls.io/github/okfn/datapackage-registry-py?branch=master)

datapackage-registry-py
=======================

A Python library for working with a Data Package Registry.

The default registry backend is currently located at:
<https://rawgit.com/dataprotocols/registry/master/registry.csv>

Usage
-----

```python
import datapackage_registry

# get the default registry objects
registry = datapackage_registry.Registry()

# see the available profiles in the registry
print(registry.available_profiles)
# {
#     'base': {
#         'id': 'base',
#         'schema': 'https://rawgit.com/dataprotocols/schemas/master/data-package.json',
#         'specification': 'http://dataprotocols.org/data-packages',
#         'title': 'Data Package'
#     },
#     'tabular': {
#         'id': 'tabular',
#         'schema': 'https://rawgit.com/dataprotocols/schemas/master/tabular-data-package.json',
#         'specification': 'http://dataprotocols.org/tabular-data-package/',
#         'title': 'Tabular Data Package'
#    }
# }

# get a profile by its id
base_profile = registry.get('base')
```

If you’d like to use a custom registry, you can pass its URL or local
path to the `Registry()` constructor, as in:

```python
import datapackage_registry

registry = datapackage_registry.Registry('http://someplace.com/my-registry.csv')
```

If you’d like to get a schema that's not in the registry, you can pass its URL
or local path to `Registry().get_external()` method, as in:

```python
import datapackage_registry
registry = datapackage_registry.Registry()

schema = registry.get_external('http://someplace.com/schema.json')
if schema is None:
    pass  # There was some error loading the schema
```

Developer notes
---------------

These notes are intended to help people that want to contribute to this
package itself. If you just want to use it, you can safely ignore this.

### Updating the local schemas cache

We cache the schemas from <https://github.com/dataprotocols/schemas>
using git-subtree. To update it, use:

    git subtree pull --prefix datapackage_registry/schemas https://github.com/dataprotocols/schemas.git master --squash

# DataPackage.py

[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)
[![Build Status](https://travis-ci.org/frictionlessdata/datapackage-py.svg?branch=master)](https://travis-ci.org/frictionlessdata/datapackage-py)
[![Windows Build Status](https://ci.appveyor.com/api/projects/status/github/frictionlessdata/datapackage-py?branch=master&svg=true)](https://ci.appveyor.com/project/vitorbaptista/datapackage-py)
[![Test Coverage](https://coveralls.io/repos/frictionlessdata/datapackage-py/badge.svg?branch=master&service=github)](https://coveralls.io/github/frictionlessdata/datapackage-py)
![Support Python versions 2.7, 3.3, 3.4 and 3.5](https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5-blue.svg)

A model for working with [Data Packages].

  [Data Packages]: http://dataprotocols.org/data-packages/
  
## Install

```
pip install datapackage
```

## Examples


### Reading a Data Package and its resource

```python
import datapackage

dp = datapackage.DataPackage('http://data.okfn.org/data/core/gdp/datapackage.json')
brazil_gdp = [{'Year': int(row['Year']), 'Value': float(row['Value'])}
              for row in dp.resources[0].data if row['Country Code'] == 'BRA']

max_gdp = max(brazil_gdp, key=lambda x: x['Value'])
min_gdp = min(brazil_gdp, key=lambda x: x['Value'])
percentual_increase = max_gdp['Value'] / min_gdp['Value']

msg = (
    'The highest Brazilian GDP occured in {max_gdp_year}, when it peaked at US$ '
    '{max_gdp:1,.0f}. This was {percentual_increase:1,.2f}% more than its '
    'minimum GDP in {min_gdp_year}.'
).format(max_gdp_year=max_gdp['Year'],
         max_gdp=max_gdp['Value'],
         percentual_increase=percentual_increase,
         min_gdp_year=min_gdp['Year'])

print(msg)
# The highest Brazilian GDP occured in 2011, when it peaked at US$ 2,615,189,973,181. This was 172.44% more than its minimum GDP in 1960.
```

### Validating a Data Package

```python
import datapackage

dp = datapackage.DataPackage('http://data.okfn.org/data/core/gdp/datapackage.json')
try:
    dp.validate()
except datapackage.exceptions.ValidationError as e:
    # Handle the ValidationError
    pass
```

### Retrieving all validation errors from a Data Package

```python
import datapackage

# This metadata has two errors:
#   * It has no "name", which is required;
#   * Its resource has no "data", "path" or "url".
metadata = {
    'resources': [
        {},
    ]
}

dp = datapackage.DataPackage(metadata)

for error in dp.iter_errors():
    # Handle error
```

### Creating a Data Package

```python
import datapackage

dp = datapackage.DataPackage()
dp.metadata['name'] = 'my_sleep_duration'
dp.metadata['resources'] = [
    {'name': 'data'}
]

resource = dp.resources[0]
resource.metadata['data'] = [
    7, 8, 5, 6, 9, 7, 8
]

with open('datapackage.json', 'w') as f:
  f.write(dp.to_json())
# {"name": "my_sleep_duration", "resources": [{"data": [7, 8, 5, 6, 9, 7, 8], "name": "data"}]}
```

### Using a schema that's not in the local cache

```python
import datapackage
import datapackage.registry

# This constant points to the official registry URL
# You can use any URL or path that points to a registry CSV
registry_url = datapackage.registry.Registry.DEFAULT_REGISTRY_URL
registry = datapackage.registry.Registry(registry_url)

metadata = {}  # The datapackage.json file
schema = registry.get('tabular')  # Change to your schema ID

dp = datapackage.DataPackage(metadata, schema)
```

### Push/pull Data Package to storage

Package provides `push_datapackage` and `pull_datapackage` utilities to
push and pull to/from storage.

This functionality requires `jsontableschema` storage plugin installed. See
[plugins](#https://github.com/frictionlessdata/jsontableschema-py#plugins)
section of `jsontableschema` docs for more information. Let's imagine
we have installed `jsontableschema-mystorage` (not a real name) plugin.

Then we could push and pull datapackage to/from the storage:

> All parameters should be used as keyword arguments.

```python
from datapackage import push_datapackage, pull_datapackage

# Push
push_datapackage(
    descriptor='descriptor_path',
    backend='mystorage', **<mystorage_options>)

# Import
pull_datapackage(
    descriptor='descriptor_path', name='datapackage_name',
    backend='mystorage', **<mystorage_options>)
```

Options could be a SQLAlchemy engine or a BigQuery project and dataset name etc.
Detailed description you could find in a concrete plugin documentation.

See concrete examples in
[plugins](#https://github.com/frictionlessdata/jsontableschema-py#plugins)
section of `jsontableschema` docs.

## Developer notes

These notes are intended to help people that want to contribute to this
package itself. If you just want to use it, you can safely ignore them.

### Updating the local schemas cache

We cache the schemas from <https://github.com/dataprotocols/schemas>
using git-subtree. To update it, use:

    git subtree pull --prefix datapackage/schemas https://github.com/dataprotocols/schemas.git master --squash

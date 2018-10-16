# datapackage-py

[![Travis](https://travis-ci.org/frictionlessdata/datapackage-py.svg?branch=master)](https://travis-ci.org/frictionlessdata/datapackage-py)
[![Coveralls](https://coveralls.io/repos/github/frictionlessdata/datapackage-py/badge.svg?branch=master)](https://coveralls.io/github/frictionlessdata/datapackage-py?branch=master)
[![PyPi](https://img.shields.io/pypi/v/datapackage.svg)](https://pypi.python.org/pypi/datapackage)
[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)

A library for working with [Data Packages](http://specs.frictionlessdata.io/data-package/).

## Features

 - `Package` class for working with data packages
 - `Resource` class for working with data resources
 - `Profile` class for working with profiles
 - `validate` function for validating data package descriptors
 - `infer` function for inferring data package descriptors

## Getting Started

### Installation

The package use semantic versioning. It means that major versions  could include breaking changes. It's highly recommended to specify `datapackage` version range in your `setup/requirements` file e.g. `datapackage>=1.0,<2.0`.

```bash
$ pip install datapackage
```

### Examples

Code examples in this readme requires Python 3.3+ interpreter. You could see even more example in [examples](https://github.com/frictionlessdata/datapackage-py/tree/master/examples) directory.

```python
from datapackage import Package

package = Package('datapackage.json')
package.getResource('resource').read()
```

## Documentation

### Package

A class for working with data packages. It provides various capabilities like loading local or remote data package, inferring a data package descriptor, saving a data package descriptor and many more.

Consider we have some local csv files in a `data` directory. Let's create a data package based on this data using a `Package` class:

> data/cities.csv

```csv
city,location
london,"51.50,-0.11"
paris,"48.85,2.30"
rome,"41.89,12.51"
```

> data/population.csv

```csv
city,year,population
london,2017,8780000
paris,2017,2240000
rome,2017,2860000
```

First we create a blank data package:

```python
package = Package()
```

Now we're ready to infer a data package descriptor based on data files we have. Because we have two csv files we use glob pattern `**/*.csv`:

```python
package.infer('**/*.csv')
package.descriptor
#{ profile: 'tabular-data-package',
#  resources:
#   [ { path: 'data/cities.csv',
#       profile: 'tabular-data-resource',
#       encoding: 'utf-8',
#       name: 'cities',
#       format: 'csv',
#       mediatype: 'text/csv',
#       schema: [Object] },
#     { path: 'data/population.csv',
#       profile: 'tabular-data-resource',
#       encoding: 'utf-8',
#       name: 'population',
#       format: 'csv',
#       mediatype: 'text/csv',
#       schema: [Object] } ] }
```

An `infer` method has found all our files and inspected it to extract useful metadata like profile, encoding, format, Table Schema etc. Let's tweak it a little bit:

```python
package.descriptor['resources'][1]['schema']['fields'][1]['type'] = 'year'
package.commit()
package.valid # true
```

Because our resources are tabular we could read it as a tabular data:

```python
package.get_resource('population').read(keyed=True)
#[ { city: 'london', year: 2017, population: 8780000 },
#  { city: 'paris', year: 2017, population: 2240000 },
#  { city: 'rome', year: 2017, population: 2860000 } ]
```

Let's save our descriptor on the disk as a zip-file:

```python
package.save('datapackage.zip')
```

To continue the work with the data package we just load it again but this time using local `datapackage.zip`:

```python
package = Package('datapackage.zip')
# Continue the work
```

It was onle basic introduction to the `Package` class. To learn more let's take a look on `Package` class API reference.

#### `Package(descriptor=None, base_path=None, strict=False, storage=None, **options)`

Constructor to instantiate `Package` class.

- `descriptor (str/dict)` - data package descriptor as local path, url or object
- `base_path (str)` - base path for all relative paths
- `strict (bool)` - strict flag to alter validation behavior. Setting it to `True` leads to throwing errors on any operation with invalid descriptor
- `storage (str/tableschema.Storage)` - storage name like `sql` or storage instance
- `options (dict)` - storage options to use for storage creation
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(Package)` - returns data package class instance

#### `package.valid`

- `(bool)` - returns validation status. It always true in strict mode.

#### `package.errors`

- `(Exception[])` - returns validation errors. It always empty in strict mode.

#### `package.profile`

- `(Profile)` - returns an instance of `Profile` class (see below).

#### `package.descriptor`

- `(dict)` - returns data package descriptor

#### `package.base_path`

- `(str/None)` - returns the data package base path

#### `package.resources`

- `(Resource[])` - returns an array of `Resource` instances (see below).

#### `package.resource_names`

- `(str[])` - returns an array of resource names.

#### `package.get_resource(name)`

Get data package resource by name.

- `name (str)` - data resource name
- `(Resource/None)` - returns `Resource` instances or null if not found

#### `package.add_resource(descriptor)`

Add new resource to data package. The data package descriptor will be validated  with newly added resource descriptor.

- `descriptor (dict)` - data resource descriptor
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(Resource/None)` - returns added `Resource` instance or null if not added

#### `package.remove_resource(name)`

Remove data package resource by name. The data package descriptor will be validated after resource descriptor removal.

- `name (str)` - data resource name
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(Resource/None)` - returns removed `Resource` instances or null if not found


#### `package.infer(pattern=False)`

> Argument `pattern` works only for local files

Infer a data package metadata. If `pattern` is not provided only existent resources will be inferred (added metadata like encoding, profile etc). If `pattern` is provided new resoures with file names mathing the pattern will be added and inferred. It commits changes to data package instance.

- `pattern (str)` - glob pattern for new resources
- `(dict)` - returns data package descriptor

#### `package.commit(strict=None)`

Update data package instance if there are in-place changes in the descriptor.

- `strict (bool)` - alter `strict` mode for further work
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(bool)` - returns true on success and false if not modified

```python
package = Package({
    'name': 'package',
    'resources': [{'name': 'resource', 'data': ['data']}]
})

package.name # package
package.descriptor['name'] = 'renamed-package'
package.name # package
package.commit()
package.name # renamed-package
```

#### `package.save(target=None, storage=None, **options)`

Saves this data package to storage if `storage` argument is passed or saves this data package's descriptor to json file if `target` arguments ends with `.json` or saves this data package to zip file otherwise.

- `target (string/filelike)` - the file path or a file-like object where the contents of this Data Package will be saved into.
- `storage (str/tableschema.Storage)` - storage name like `sql` or storage instance
- `options (dict)` - storage options to use for storage creation
- `(exceptions.DataPackageException)` - raises if there was some error writing the package
- `(bool)` - return true on success

It creates a zip file into ``file_or_path`` with the contents of this Data Package and its resources. Every resource which content lives in the local filesystem will be copied to the zip file. Consider the following Data Package descriptor:

```json
{
    "name": "gdp",
    "resources": [
        {"name": "local", "format": "CSV", "path": "data.csv"},
        {"name": "inline", "data": [4, 8, 15, 16, 23, 42]},
        {"name": "remote", "url": "http://someplace.com/data.csv"}
    ]
}
```

The final structure of the zip file will be:

```
./datapackage.json
./data/local.csv
```

With the contents of `datapackage.json` being the same as returned `datapackage.descriptor`. The resources' file names are generated based on their `name` and `format` fields if they exist. If the resource has no `name`, it'll be used `resource-X`, where `X` is the index of the resource in the `resources` list (starting at zero). If the resource has `format`, it'll be lowercased and appended to the `name`, becoming "`name.format`".

### Resource

A class for working with data resources. You can read or iterate tabular resources using the `iter/read` methods and all resource as bytes using `row_iter/row_read` methods.

Consider we have some local csv file. It could be inline data or remote link - all supported by `Resource` class (except local files for in-brower usage of course). But say it's `data.csv` for now:

```csv
city,location
london,"51.50,-0.11"
paris,"48.85,2.30"
rome,N/A
```

Let's create and read a resource. Because resource is tabular we could use `resource.read` method with a `keyed` option to get an array of keyed rows:

```python
resource = Resource({path: 'data.csv'})
resource.tabular # true
resource.headers # ['city', 'location']
resource.read(keyed=True)
# [
#   {city: 'london', location: '51.50,-0.11'},
#   {city: 'paris', location: '48.85,2.30'},
#   {city: 'rome', location: 'N/A'},
# ]
```

As we could see our locations are just a strings. But it should be geopoints. Also Rome's location is not available but it's also just a `N/A` string instead of Python `None`. First we have to infer resource metadata:

```python
resource.infer()
resource.descriptor
#{ path: 'data.csv',
#  profile: 'tabular-data-resource',
#  encoding: 'utf-8',
#  name: 'data',
#  format: 'csv',
#  mediatype: 'text/csv',
# schema: { fields: [ [Object], [Object] ], missingValues: [ '' ] } }
resource.read(keyed=True)
# Fails with a data validation error
```

Let's fix not available location. There is a `missingValues` property in Table Schema specification. As a first try we set `missingValues` to `N/A` in `resource.descriptor.schema`. Resource descriptor could be changed in-place but all changes should be commited by `resource.commit()`:

```python
resource.descriptor['schema']['missingValues'] = 'N/A'
resource.commit()
resource.valid # False
resource.errors
# [<ValidationError: "'N/A' is not of type 'array'">]
```

As a good citiziens we've decided to check out recource descriptor validity. And it's not valid! We should use an array for `missingValues` property. Also don't forget to have an empty string as a missing value:

```python
resource.descriptor['schema']['missingValues'] = ['', 'N/A']
resource.commit()
resource.valid # true
```

All good. It looks like we're ready to read our data again:

```python
resource.read(keyed=True)
# [
#   {city: 'london', location: [51.50,-0.11]},
#   {city: 'paris', location: [48.85,2.30]},
#   {city: 'rome', location: null},
# ]
```

Now we see that:
- locations are arrays with numeric lattide and longitude
- Rome's location is a native JavaScript `null`

And because there are no errors on data reading we could be sure that our data is valid againt our schema. Let's save our resource descriptor:

```python
resource.save('dataresource.json')
```

Let's check newly-crated `dataresource.json`. It contains path to our data file, inferred metadata and our `missingValues` tweak:

```json
{
    "path": "data.csv",
    "profile": "tabular-data-resource",
    "encoding": "utf-8",
    "name": "data",
    "format": "csv",
    "mediatype": "text/csv",
    "schema": {
        "fields": [
            {
                "name": "city",
                "type": "string",
                "format": "default"
            },
            {
                "name": "location",
                "type": "geopoint",
                "format": "default"
            }
        ],
        "missingValues": [
            "",
            "N/A"
        ]
    }
}
```

If we decide to improve it even more we could update the `dataresource.json` file and then open it again using local file name:

```python
resource = Resource('dataresource.json')
# Continue the work
```

It was onle basic introduction to the `Resource` class. To learn more let's take a look on `Resource` class API reference.

#### `Resource(descriptor={}, base_path=None, strict=False, storage=None, **options)`

Constructor to instantiate `Resource` class.

- `descriptor (str/dict)` - data resource descriptor as local path, url or object
- `base_path (str)` - base path for all relative paths
- `strict (bool)` - strict flag to alter validation behavior. Setting it to `true` leads to throwing errors on any operation with invalid descriptor
- `storage (str/tableschema.Storage)` - storage name like `sql` or storage instance
- `options (dict)` - storage options to use for storage creation
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(Resource)` - returns resource class instance

#### `resource.valid`

- `(bool)` - returns validation status. It always true in strict mode.

#### `resource.errors`

- `(Exception[])` - returns validation errors. It always empty in strict mode.

#### `resource.profile`

- `(Profile)` - returns an instance of `Profile` class (see below).

#### `resource.descriptor`

- (dict) - returns resource descriptor

#### `resource.name`

- `(str)` - returns resource name

#### `resource.inline`

- `(bool)` - returns true if resource is inline

#### `resource.local`

- `(bool)` - returns true if resource is local

#### `resource.remote`

- `(bool)` - returns true if resource is remote

#### `resource.multipart`

- `(bool)` - returns true if resource is multipart

#### `resource.tabular`

- `(bool)` - returns true if resource is tabular

#### `resource.source`

- `(list/str)` - returns `data` or `path` property

Combination of `resource.source` and `resource.inline/local/remote/multipart` provides predictable interface to work with resource data.

#### `resource.headers`

> Only for tabular resources

- `(str[])` - returns data source headers

#### `resource.schema`

> Only for tabular resources

For tabular resources it returns `Schema` instance to interact with data schema. Read API documentation - [tableschema.Schema](https://github.com/frictionlessdata/tableschema-py#schema).

- `(tableschema.Schema)` - returns schema class instance

#### `resource.iter(keyed=False, extended=False, cast=True, relations=False)`

> Only for tabular resources

Iter through the table data and emits rows cast based on table schema (async for loop). Data casting could be disabled.

- `keyed (bool)` - iter keyed rows
- `extended (bool)` - iter extended rows
- `cast (bool)` - disable data casting if false
- `relations (bool)` - if true foreign key fields will be checked and resolved to its references
- `(exceptions.DataPackageException)` - raises any error occured in this process
- `(any[]/any{})` - yields rows:
  - `[value1, value2]` - base
  - `{header1: value1, header2: value2}` - keyed
  - `[rowNumber, [header1, header2], [value1, value2]]` - extended

#### `resource.read(keyed=False, extended=False, cast=True, relations=False, limit=None)`

> Only for tabular resources

Read the whole table and returns as array of rows. Count of rows could be limited.

- `keyed (bool)` - flag to emit keyed rows
- `extended (bool)` - flag to emit extended rows
- `cast (bool)` - flag to disable data casting if false
- `relations (bool)` - if true foreign key fields will be checked and resolved to its references
- `limit (int)` - integer limit of rows to return
- `(exceptions.DataPackageException)` - raises any error occured in this process
- `(list[])` - returns array of rows (see `table.iter`)

#### `resource.check_relations()`

> Only for tabular resources

It checks foreign keys and raises an exception if there are integrity issues.

- `(exceptions.RelationError)` - raises if there are integrity issues
- `(bool)` - returns True if no issues

#### `resource.raw_iter(stream=False)`

Iterate over data chunks as bytes. If `stream` is true File-like object will be returned.

- `stream (bool)` - File-like object will be returned
- `(bytes[]/filelike)` - returns bytes[]/filelike

#### `resource.raw_read()`

Returns resource data as bytes.

- (bytes) - returns resource data in bytes

#### `resource.infer(**options)`

Infer resource metadata like name, format, mediatype, encoding, schema and profile. It commits this changes into resource instance.

- `options` - options will be passed to `tableschema.infer` call, for more control on results (e.g. for setting `limit`, `confidence` etc.).

- `(dict)` - returns resource descriptor

#### `resource.commit(strict=None)`

Update resource instance if there are in-place changes in the descriptor.

- `strict (bool)` - alter `strict` mode for further work
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(bool)` - returns true on success and false if not modified

#### `resource.save(target, storage=None, **options)`

Saves this resource into storage if `storage` argument is passed or saves this resource's descriptor to json file otherwise.

- `target (str)` - path where to save a resource
- `storage (str/tableschema.Storage)` - storage name like `sql` or storage instance
- `options (dict)` - storage options to use for storage creation
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(bool)` - returns true on success

### Profile

A component to represent JSON Schema profile from [Profiles Registry]( https://specs.frictionlessdata.io/schemas/registry.json):

```python
profile = Profile('data-package')

profile.name # data-package
profile.jsonschema # JSON Schema contents

try:
   valid = profile.validate(descriptor)
except exceptions.ValidationError as exception:
   for error in exception.errors:
       # handle individual error
```

#### `Profile(profile)`

Constuctor to instantiate `Profile` class.

- `profile (str)` - profile name in registry or URL to JSON Schema
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(Profile)` - returns profile class instance

#### `profile.name`

- `(str/None)` - returns profile name if available

#### `profile.jsonschema`

- `(dict)` - returns profile JSON Schema contents

#### `profile.validate(descriptor)`

Validate a data package `descriptor` against the profile.

- `descriptor (dict)` - retrieved and dereferenced data package descriptor
- `(exceptions.ValidationError)` - raises if not valid
- `(bool)` - returns True if valid

### Validate

A standalone function to validate a data package descriptor:

```python
from datapackage import validate, exceptions

try:
    valid = validate(descriptor)
except exceptions.ValidationError as exception:
   for error in exception.errors:
       # handle individual error
```

#### `validate(descriptor)`

Validate a data package descriptor.

- `descriptor (str/dict)` - package descriptor (one of):
  - local path
  - remote url
  - object
- (exceptions.ValidationError) - raises on invalid
- `(bool)` - returns true on valid

### Infer

A standalone function to infer a data package descriptor.

```python
descriptor = infer('**/*.csv')
#{ profile: 'tabular-data-resource',
#  resources:
#   [ { path: 'data/cities.csv',
#       profile: 'tabular-data-resource',
#       encoding: 'utf-8',
#       name: 'cities',
#       format: 'csv',
#       mediatype: 'text/csv',
#       schema: [Object] },
#     { path: 'data/population.csv',
#       profile: 'tabular-data-resource',
#       encoding: 'utf-8',
#       name: 'population',
#       format: 'csv',
#       mediatype: 'text/csv',
#       schema: [Object] } ] }
```

#### `infer(pattern, base_path=None)`

> Argument `pattern` works only for local files

Infer a data package descriptor.

- `pattern (str)` - glob file pattern
- `(dict)` - returns data package descriptor


### Foreign Keys

The library supports foreign keys described in the [Table Schema](http://specs.frictionlessdata.io/table-schema/#foreign-keys) specification. It means if your data package descriptor use `resources[].schema.foreignKeys` property for some resources a data integrity will be checked on reading operations.

Consider we have a data package:

```python
DESCRIPTOR = {
  'resources': [
    {
      'name': 'teams',
      'data': [
        ['id', 'name', 'city'],
        ['1', 'Arsenal', 'London'],
        ['2', 'Real', 'Madrid'],
        ['3', 'Bayern', 'Munich'],
      ],
      'schema': {
        'fields': [
          {'name': 'id', 'type': 'integer'},
          {'name': 'name', 'type': 'string'},
          {'name': 'city', 'type': 'string'},
        ],
        'foreignKeys': [
          {
            'fields': 'city',
            'reference': {'resource': 'cities', 'fields': 'name'},
          },
        ],
      },
    }, {
      'name': 'cities',
      'data': [
        ['name', 'country'],
        ['London', 'England'],
        ['Madrid', 'Spain'],
      ],
    },
  ],
}
```

Let's check relations for a `teams` resource:

```python
from datapackage import Package

package = Package(DESCRIPTOR)
teams = package.get_resource('teams')
teams.check_relations()
# tableschema.exceptions.RelationError: Foreign key "['city']" violation in row "4"
```

As we could see there is a foreign key violation. That's because our lookup table `cities` doesn't have a city of `Munich` but we have a team from there. We need to fix it in `cities` resource:

```python
package.descriptor['resources'][1]['data'].append(['Munich', 'Germany'])
package.commit()
teams = package.get_resource('teams')
teams.check_relations()
# True
```

Fixed! But not only a check operation is available. We could use `relations` argument for `resource.iter/read` methods to dereference a resource relations:

```python
teams.read(keyed=True, relations=True)
#[{'id': 1, 'name': 'Arsenal', 'city': {'name': 'London', 'country': 'England}},
# {'id': 2, 'name': 'Real', 'city': {'name': 'Madrid', 'country': 'Spain}},
# {'id': 3, 'name': 'Bayern', 'city': {'name': 'Munich', 'country': 'Germany}}]
```

Instead of plain city name we've got a dictionary containing a city data. These `resource.iter/read` methods will fail with the same as `resource.check_relations` error if there is an integrity issue. But only if `relations=True` flag is passed.

### Exceptions

#### `exceptions.DataPackageException`

Base class for all library exceptions. If there are multiple errors it could be read from an exceptions object:

```python
try:
    # lib action
except exceptions.DataPackageException as exception:
    if exception.multiple:
        for error in exception.errors:
            # handle error
```

#### `exceptions.LoadError`

All loading errors.

#### `exceptions.ValidationError`

All validation errors.

#### `exceptions.CastError`

All value cast errors.

#### `exceptions.RelationError`

All integrity errors.

#### `exceptions.StorageError`

All storage errors.

### CLI

> It's a provisional API. If you use it as a part of other program please pin concrete `datapackage` version to your requirements file.

The library ships with a simple CLI:

```bash
$ datapackage infer '**/*.csv'
Data package descriptor:
{'profile': 'tabular-data-package',
 'resources': [{'encoding': 'utf-8',
                'format': 'csv',
                'mediatype': 'text/csv',
                'name': 'data',
                'path': 'data/datapackage/data.csv',
                'profile': 'tabular-data-resource',
                'schema': ...}}]}
```

#### `$ datapackage`

```bash
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  infer
  validate
```

## Contributing

The project follows the [Open Knowledge International coding standards](https://github.com/okfn/coding-standards).

Recommended way to get started is to create and activate a project virtual environment.
To install package and development dependencies into active environment:

```
$ make install
```

To run tests with linting and coverage:

```bash
$ make test
```

For linting `pylama` configured in `pylama.ini` is used. On this stage it's already
installed into your environment and could be used separately with more fine-grained control
as described in documentation - https://pylama.readthedocs.io/en/latest/.

For example to sort results by error type:

```bash
$ pylama --sort <path>
```

For testing `tox` configured in `tox.ini` is used.
It's already installed into your environment and could be used separately with more fine-grained control as described in documentation - https://testrun.org/tox/latest/.

For example to check subset of tests against Python 2 environment with increased verbosity.
All positional arguments and options after `--` will be passed to `py.test`:

```bash
tox -e py27 -- -v tests/<path>
```

Under the hood `tox` uses `pytest` configured in `pytest.ini`, `coverage`
and `mock` packages. This packages are available only in tox envionments.

Here is a list of the library contributors:
- Tryggvi Björgvinsson <tryggvi.bjorgvinsson@okfn.org>
- Gunnlaugur Thor Briem <gunnlaugur@gmail.com>
- Edouard <edou4rd@gmail.com>
- Michael Bauer <mihi@lo-res.org>
- Alex Chandel <alexchandel@gmail.com>
- Jessica B. Hamrick <jhamrick@berkeley.edu>
- Ricardo Lafuente
- Paul Walsh <paulywalsh@gmail.com>
- Luiz Armesto <luiz.armesto@gmail.com>
- hansl <hansl@edge-net.net>
- femtotrader <femto.trader@gmail.com>
- Vitor Baptista <vitor@vitorbaptista.com>
- Bryon Jacob <bryon@data.world>

## Changelog

Here described only breaking and the most important changes. The full changelog and documentation for all released versions could be found in nicely formatted [commit history](https://github.com/frictionlessdata/datapackage-py/commits/master).

### v1.5

Updated behaviour:
- Added support for Python 3.7

### v1.4

New API added:
- added `skip_rows` support to the resource descriptor

### v1.3

New API added:
- property `package.base_path` is now publicly available

### v1.2

Updated behaviour:
- CLI command `$ datapackage infer` now outputs only a JSON-formatted data package descriptor.

### v1.1

New API added:
- Added an integration between `Package/Resource` and the `tableschema.Storage` - https://github.com/frictionlessdata/tableschema-py#storage. It allows to load and save data package from/to different storages like SQL/BigQuery/etc.

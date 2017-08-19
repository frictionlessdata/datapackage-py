# datapackage-py

[![Travis](https://travis-ci.org/frictionlessdata/datapackage-py.svg?branch=master)](https://travis-ci.org/frictionlessdata/datapackage-py)
[![Coveralls](https://coveralls.io/repos/github/frictionlessdata/datapackage-py/badge.svg?branch=master)](https://coveralls.io/github/frictionlessdata/datapackage-py?branch=master)
[![PyPi](https://img.shields.io/pypi/v/datapackage.svg)](https://pypi.python.org/pypi/datapackage)
[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)

A library for working with [Data Packages](http://specs.frictionlessdata.io/data-package/).

> Version v1.0 includes various important changes. Please read a [migration guide](#v10).

## Features

 - `Package` class for working with data packages
 - `Resource` class for working with data resources
 - `Profile` class for working with profiles
 - `validate` function for validating data package descriptors
 - `infer` function for inferring data package descriptors

### Installation

The package use semantic versioning. It means that major versions  could include breaking changes. It's highly recommended to specify `datapackage` version range in your `setup/requirements` file e.g. `datapackage>=1.0,<2.0`.

```bash
$ pip install datapackage
```

### Examples

Code examples in this readme requires Python 3.3+ interpreter. You could see even more example in [examples](https://github.com/frictionlessdata/datapacakge-py/tree/master/examples) directory.

```python
from datapackage import Package

package = Package('descriptor.json')
package.getResource('resource').table.read()
```

## Documentation

### Package

A class for working with data packages. It provides various capabilities like loading local or remote data package, inferring a data package descriptor, saving a data package descriptor and many more.

> TODO: insert tutorial here

> TODO: insert reference here

### Resource

A class for working with data resources. You can read or iterate tabular resources using the `table` property.

> TODO: insert tutorial here

#### `Resource(descriptor, basePath=None, strict=False)`

Constructor to instantiate `Resource` class.

- `descriptor (str/dict)` - data resource descriptor as local path, url or object
- `base_path (str)` - base path for all relative paths
- `strict (bool)` - strict flag to alter validation behavior. Setting it to `true` leads to throwing errors on any operation with invalid descriptor
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(Resource)` - returns resource class instance

#### `resource.valid`

- `(bool)` - returns validation status. It always true in strict mode.

#### `resource.errors`

- `(Error[])` - returns validation errors. It always empty in strict mode.

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

#### `resource.table`

For tabular resources it returns `Table` instance to interact with data table. Read API documentation - [tableschema.Table](https://github.com/frictionlessdata/tableschema-py#table).

- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(None/tableschema.Table)` - returns table instance if resource is tabular

#### `resource.iter(filelike=False)`

Iterate over data chunks as bytes. If `filelike` is true File-like object will be returned.

- `filelike (bool)` - File-like object will be returned
- `(bytes[]/filelike)` - returns byte[]/filelike

#### `resource.read()`

Returns resource data as bytes.

- (bytes) - returns resource data in bytes

#### `resource.infer()`

Infer resource metadata like name, format, mediatype, encoding, schema and profile. It commits this changes into resource instance.

- `(dict)` - returns resource descriptor

#### `resource.commit(strict=None)`

Update resource instance if there are in-place changes in the descriptor.

- `strict (bool)` - alter `strict` mode for further work
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(bool)` - returns true on success and false if not modified

#### `resource.save(target)`

> For now only descriptor will be saved.

Save resource to target destination.

- `target (str)` - path where to save a resource
- `(exceptions.DataPackageException)` - raises error if something goes wrong
- `(bool)` - returns true on success

### Profile

A component to represent JSON Schema profile from [Profiles Registry]( https://specs.frictionlessdata.io/schemas/registry.json).

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

A standalone function to validate a data package descriptor.

> TODO: insert tutorial here

> TODO: insert reference here

### Infer

A standalone function to infer a data package descriptor.

> TODO: insert tutorial here

> TODO: insert reference here

### Exceptions

> TODO: insert reference here

### CLI

> It's a provisional API. If you use it as a part of other program please pin concrete `goodtables` version to your requirements file.

The library ships with a simple CLI.

> TODO: insert reference here

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

### v1.0

This version includes various big changes. A migration guide is under development and will be published here.

### v0.8

Last pre-v1 stable version of the library.

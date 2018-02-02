# datapackage-py

[![Travis](https://travis-ci.org/frictionlessdata/datapackage-py.svg?branch=master)](https://travis-ci.org/frictionlessdata/datapackage-py)
[![Coveralls](https://coveralls.io/repos/github/frictionlessdata/datapackage-py/badge.svg?branch=master)](https://coveralls.io/github/frictionlessdata/datapackage-py?branch=master)
[![PyPi](https://img.shields.io/pypi/v/datapackage.svg)](https://pypi.python.org/pypi/datapackage)
[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)

A library for working with [Data Packages](http://specs.frictionlessdata.io/data-package/).

## Features

* Read, edit and create data packages
* **Data validation**: Validate metadata and contents of data packages
* **Generate data packages from data files**: With the path for one or more files, you can automatically create a data package, including an inferred schema for tabular files, using the `infer()` method

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
## Table of Contents

- [Features](#features)
- [Getting started](#getting-started)
    - [Installation](#installation)
    - [Running on Python](#running-on-python)
    - [Running on CLI](#running-on-cli)
- [Documentation](#documentation)
    - [Semantic versioning](#semantic-versioning)
    - [Package](#package)
    - [Resource](#resource)
    - [Foreign Keys](#foreign-keys)
    - [Profile](#profile)
- [API Reference](#api-reference)
- [Contributing](#contributing)

<!-- markdown-toc end -->

## Getting started

### Installation

```bash
$ pip install datapackage
```

### Running on Python

```python
from datapackage import Package

package = Package('datapackage.json')
package.getResource('resource').read()
```

You can find other examples in the [examples][examples-dir] directory.

### Running on CLI

This library ships with a simple CLI named `datapackage`. If you call it without passing any arguments, it will print the help text:

```bash
Usage: datapackage [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  infer
  validate
```

The `infer` command creates a datapackage with the resources passed as arguments, inferring their schema.

The `validate` command validates that the data package descriptor is valid, not its contents. If you want to validate tabular data packages, check the [goodtables][goodtables] library.

## Documentation

In the following sections, we'll walk through some usage examples of
this library. All examples were tested with Python 3.6, but should
run fine with Python 3.3+.

### Semantic versioning

We follow the [Semantic Versioning][semver] specification to define our version
numbers. This means that we'll increase the major version number when there's a
breaking change. Because of this, we recommend you to explicitly specify the
library version on your dependency list (e.g. `setup.py` or
`requirements.txt`).

### Package

This is the most important class. It represents the data package, and provides
functionality to create, load, and save data packages, infer its descriptor
from the data, and others. Let's see an example.

Consider we have the CSV `data/cities.csv` as:

```csv
city,location
london,"51.50,-0.11"
paris,"48.85,2.30"
rome,"41.89,12.51"
```

And `data/population.csv` as:

```csv
city,year,population
london,2017,8780000
paris,2017,2240000
rome,2017,2860000
```

Our final objective is to create a data package containing these files. First,
we create a blank data package:

```python
package = Package()
```

Now we're ready to infer the data package based on our data files. As we have
multiple data files inside a `data` folder, we can use the pattern
`data/*.csv`:

```python
package.infer('data/*.csv')
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

The `infer` method found our files and inferred their metadata like profile,
encoding, format, Table Schema, etc. This is already a valid data package, and
we could save it and stop here. Before doing that, let's tweak it a bit:

```python
package.descriptor['resources'][1]['schema']['fields'][1]['type'] = 'year'
package.commit()  # The descriptor changes are only effective after calling .commit()
package.valid  # The data package is still valid
```

As our resources are tabular, we can read each row with:

```python
package.get_resource('population').read(keyed=True)
#[ { city: 'london', year: 2017, population: 8780000 },
#  { city: 'paris', year: 2017, population: 2240000 },
#  { city: 'rome', year: 2017, population: 2860000 } ]
```

We can now save the data package as a ZIP with:

```python
package.save('datapackage.zip')
```

The resulting ZIP will have the `datapackage.json` descriptor and the data files. Later, if we want to work with this data package again, we can just load this ZIP as:

```python
package = Package('datapackage.zip')
```

This was only a basic introduction to the `datapackage.Package` class. The full API reference is available below.

### Resource

This class is responsible for loading and modifiying the data files contents and metadata. You can read and iterate on tabular resources using the `iter` and `read` methods, and all resource types as bytes using `row_iter` and `row_read` methods.

Considering we have the following `data.csv` local file (it also supports remote URIs or Python objects):

```csv
city,location
london,"51.50,-0.11"
paris,"48.85,2.30"
rome,N/A
```

To read this file, we can do:

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

Everything was loaded correctly. As it's a tabular file, we could use the `.read(keyed=True)` method to load it as an array of dicts. Looking at the data itself, we see that everything was loaded as strings. This is correct for the `city`, but `location` is a latitude and longitude pair, and it has a value `N/A` that represents an inexistent value. Ideally, it would simply be `None`.

Let's improve this. First, we have to infer the resource's metadata:

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

The validation error is caused because, although the inferring method correctly figured out that `latitude` is a `geopoint` column, it didn't know how to handle the `N/A` value. We need to tell it to treat `N/A` as a null value. To do so, we will change the `missingValue` property of our schema. Let's try it:

```python
resource.descriptor['schema']['missingValues'] = 'N/A'
resource.commit()  # Changes to the descriptor only take effect after .commit()
resource.valid # False
resource.errors
# [<ValidationError: "'N/A' is not of type 'array'">]
```

That didn't work out. The problem is that the `missingValues` property must be an array, as we can have more than one. Let's try again, but this time also add the empty string as a missing value.

```python
resource.descriptor['schema']['missingValues'] = ['', 'N/A']
resource.commit()
resource.valid # true
```

All good. We're ready to read our data again:

```python
resource.read(keyed=True)
# [
#   {city: 'london', location: [51.50, -0.11]},
#   {city: 'paris', location: [48.85, 2.30]},
#   {city: 'rome', location: None},
# ]
```

Now we see that:

- Locations are arrays with numeric latitude and longitude
- Rome's location is `None`

And because there were no errors on reading the data, we can be sure that our data is valid against the schema. Let's save our resource descriptor:

```python
resource.save('dataresource.json')
```

The generated `dataresource.json` contains path to our data file, the inferred metadata, and our `missingValues` tweak:

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

If we want to work with this resource again, we can load it with:

```python
resource = Resource('dataresource.json')
```

This was only a basic introduction to the `Resource` class. The full API reference is available below.

### Foreign Keys

This library supports foreign keys as described in the [Table
Schema](http://specs.frictionlessdata.io/table-schema/#foreign-keys)
specification. If your data package descriptor contains the
`resources[].schema.foreignKeys` property for some resource, its data integrity
will be checked during the read operations.

Consider the following `datapackage.json`:

```python
{
  "resources": [
    {
      "name": "teams",
      "data": [
        ["id", "name", "city"],
        ["1", "Arsenal", "London"],
        ["2", "Real", "Madrid"],
        ["3", "Bayern", "Munich"],
      ],
      "schema": {
        "fields": [
          {"name": "id", "type": "integer"},
          {"name": "name", "type": "string"},
          {"name": "city", "type": "string"},
        ],
        "foreignKeys": [
          {
            "fields": "city",
            "reference": {"resource": "cities", "fields": "name"},
          },
        ],
      },
    },
    {
      "name": "cities",
      "data": [
        ["name", "country"],
        ["London", "England"],
        ["Madrid", "Spain"],
      ],
    },
  ],
}
```

Let's check the relations for the `teams` resource:

```python
from datapackage import Package

package = Package('datapackage.json')
teams = package.get_resource('teams')
teams.check_relations()
# tableschema.exceptions.RelationError: Foreign key "['city']" violation in row "4"
```

There is a foreign key violation. That's because our resource `cities` doesn't have the city `Munich`, but we have a team from there. We can add it as:

```python
package.descriptor['resources'][1]['data'].append(['Munich', 'Germany'])
package.commit()
teams = package.get_resource('teams')
teams.check_relations()
# True
```

Fixed! Next, what if we wanted to iterate over the teams and get their countries? The `iter()` and `read()` methods provide a boolean `relations` argument to dereference the resource's relations. For example:

```python
teams.read(keyed=True, relations=True)
#[{'id': 1, 'name': 'Arsenal', 'city': {'name': 'London', 'country': 'England}},
# {'id': 2, 'name': 'Real', 'city': {'name': 'Madrid', 'country': 'Spain}},
# {'id': 3, 'name': 'Bayern', 'city': {'name': 'Munich', 'country': 'Germany}}]
```

Instead of just the city name, the `city` element now has all the contents from
the `cities` resource, so we can get a team's home country via
`team['city']['country']`.

When calling these `iter()` and `read()` methods with the `relations=True`
argument, they will call `check_relations()` themselves, failing if there is an
integrity issue.

### Profile

Represents a JSON Schema profile from the [Profiles Registry][profile-registry]:

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

## API Reference

The API reference is written as docstrings. The main classes are
[Package][file:package] and [Resource][file:resource]. You
can also see a list of all exceptions thrown in the
[datapackage/exceptions.py][file:exceptions] file.

## Contributing

This project follows the [Open Knowledge International coding standards](https://github.com/okfn/coding-standards).

The recommended way to get started is to create and activate a project virtual environment using `virtualenv`. Then you can install the development dependencies via:

```bash
$ make install
```

To run the tests, use:

```bash
$ make test
```

This will run all tests, in all supported Python versions, and lint the code.
Under the hood we're using `tox`, so if you prefer you can call it directly.
It's specially useful when you want to run a single Python version, for
example (e.g.  `tox -e py36`).

### Contributors

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

[goodtables]: https://github.com/frictionlessdata/goodtables-py "Goodtables"
[examples-dir]: examples "Datapackage Library Examples"
[profile-registry]: https://specs.frictionlessdata.io/schemas/registry.json "Frictionless Data Profile Registry"
[tableschema-py]: https://github.com/frictionlessdata/tableschema-py#schema "Table Schema"
[semver]: https://semver.org/ "Semantic Versioning"
[file:package]: datapackage/package.py
[file:resource]: datapackage/resource.py
[file:exceptions]: datapackage/exceptions.py

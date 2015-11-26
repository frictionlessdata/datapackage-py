#JSON Schemas for Data Protocol Formats

[![Build Status](https://travis-ci.org/dataprotocols/schemas.svg?branch=master)](https://travis-ci.org/dataprotocols/schemas)

This project provides schemas for several of the simple data formats published as part of the [Data Protocols](http://dataprotocols.org/) effort.

The schemas have been implemented using the [JSON Schema](http://json-schema.org/) specification which provides a simple declarative format for describing the structure of JSON documents.

The following schemas have been created:

* `data-package.json` -- [datapackage.json](http://dataprotocols.org/data-packages/) package files
* `json-table-schema.json` -- [JSON Table Schemas](http://dataprotocols.org/json-table-schema/) objects
* `csv-dialect-description-format.json` -- for validating [CSV Dialect Description Format](http://dataprotocols.org/csv-dialect/) `dialect` objects

The schemas can be used as standalone schemas or combined to carry out validation of more complex documents, e.g. those that conform to the Tabular Data Package specification.

## Registry

The registry is a CSV file ([registry.csv](registry.csv)) that contains
metadata about the schemas. It has the following attributes:

| name          | description                                         | example                                                                                  |
| ------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| id            | locally unique identifier                           | tabular                                                                                  |
| title         | human-readable name                                 | Tabular Data Package                                                                     |
| schema        | URL to the related JSON Schema                      | https://raw.githubusercontent.com/dataprotocols/schemas/master/tabular-data-package.json |
| schema_path   | Path to the schema relative to this registry's path | tabular-data-package.json                                                                |
| specification | URL to the human-readable specification             | http://dataprotocols.org/tabular-data-package/                                           |

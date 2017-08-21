.PHONY: all install list specs test version


PACKAGE := $(shell grep '^PACKAGE =' setup.py | cut -d "'" -f2)
VERSION := $(shell head -n 1 $(PACKAGE)/VERSION)


all: list

install:
	pip install --upgrade -e .[develop]

list:
	@grep '^\.PHONY' Makefile | cut -d' ' -f2- | tr ' ' '\n'

profiles:
	wget -O datapackage/profiles/registry.json https://specs.frictionlessdata.io/schemas/registry.json
	wget -O datapackage/profiles/data-package.json https://specs.frictionlessdata.io/schemas/data-package.json
	wget -O datapackage/profiles/tabular-data-package.json https://specs.frictionlessdata.io/schemas/tabular-data-package.json
	wget -O datapackage/profiles/fiscal-data-package.json https://specs.frictionlessdata.io/schemas/fiscal-data-package.json
	wget -O datapackage/profiles/data-resource.json https://specs.frictionlessdata.io/schemas/data-resource.json
	wget -O datapackage/profiles/tabular-data-resource.json https://specs.frictionlessdata.io/schemas/tabular-data-resource.json

test:
	pylama $(PACKAGE)
	tox

version:
	@echo $(VERSION)

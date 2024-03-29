.PHONY: all install list readme release templates test version


PACKAGE := $(shell grep '^PACKAGE =' setup.py | cut -d "'" -f2)
VERSION := $(shell head -n 1 $(PACKAGE)/VERSION)
LEAD := $(shell head -n 1 LEAD.md)


all: list

install:
	pip install setuptools
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

readme:
	pip install md-toc
	pip install referencer
	referencer $(PACKAGE) README.md --in-place
	md_toc -p github --header-levels 3 README.md
	sed -i '/(#$(PACKAGE)-py)/,+2d' README.md

release:
	git checkout master && git pull origin && git fetch -p
	@git log --pretty=format:"%C(yellow)%h%Creset %s%Cgreen%d" --reverse -20
	@echo "\nReleasing v$(VERSION) in 10 seconds. Press <CTRL+C> to abort\n" && sleep 10
	git commit -a -m 'v$(VERSION)' && git tag -a v$(VERSION) -m 'v$(VERSION)'
	git push --follow-tags

templates:
	sed -i -E "s/@(\w*)/@$(LEAD)/" .github/issue_template.md
	sed -i -E "s/@(\w*)/@$(LEAD)/" .github/pull_request_template.md

test:
	pylama $(PACKAGE)
	pytest --cov ${PACKAGE} --cov-report term-missing --cov-fail-under 80

version:
	@echo $(VERSION)

.PHONY: specs


specs:
	wget -O datapackage/profiles/registry.json https://specs.frictionlessdata.io/schemas/registry.json
	wget -O datapackage/profiles/data-package.json https://specs.frictionlessdata.io/schemas/data-package.json
	wget -O datapackage/profiles/tabular-data-package.json https://specs.frictionlessdata.io/schemas/tabular-data-package.json
	wget -O datapackage/profiles/fiscal-data-package.json https://specs.frictionlessdata.io/schemas/fiscal-data-package.json

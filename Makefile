.PHONY: specs


specs:
	wget -O datapackage/specs/registry.json https://specs.frictionlessdata.io/schemas/registry.json
	wget -O datapackage/specs/data-package.json https://specs.frictionlessdata.io/schemas/data-package.json
	wget -O datapackage/specs/tabular-data-package.json https://specs.frictionlessdata.io/schemas/tabular-data-package.json
	wget -O datapackage/specs/fiscal-data-package.json https://specs.frictionlessdata.io/schemas/fiscal-data-package.json

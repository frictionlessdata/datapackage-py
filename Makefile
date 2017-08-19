.PHONY: specs


profiles:
	wget -O datapackage/profiles/registry.json https://specs.frictionlessdata.io/schemas/registry.json
	wget -O datapackage/profiles/data-package.json https://specs.frictionlessdata.io/schemas/data-package.json
	wget -O datapackage/profiles/tabular-data-package.json https://specs.frictionlessdata.io/schemas/tabular-data-package.json
	wget -O datapackage/profiles/fiscal-data-package.json https://specs.frictionlessdata.io/schemas/fiscal-data-package.json
	wget -O datapackage/profiles/data-resource.json https://specs.frictionlessdata.io/schemas/data-resource.json
	wget -O datapackage/profiles/tabular-data-resource.json https://specs.frictionlessdata.io/schemas/tabular-data-resource.json

from copy import deepcopy
from itertools import chain
from . import exceptions


# Module API

class Group(object):

    # Public

    def __init__(self, resources):

        # Contract checks
        assert resources
        assert all([resource.group for resource in resources])
        assert all([resource.tabular for resource in resources])

        # Get props from the resources
        self.__name = resources[0].descriptor['group']
        self.__headers = resources[0].headers
        self.__schema = resources[0].schema
        self.__resources = resources

    @property
    def name(self):
        """https://github.com/frictionlessdata/datapackage-py#group
        """
        return self.__name

    @property
    def headers(self):
        """https://github.com/frictionlessdata/datapackage-py#group
        """
        return self.__headers

    @property
    def schema(self):
        """https://github.com/frictionlessdata/datapackage-py#group
        """
        return self.__schema

    def iter(self, **options):
        return chain([resource.iter(**options) for resource in resources])

    def read(self, limit=None, **options):
        rows = []
        for count, row in enumerate(self.iter(**options), start=1):
            rows.append(row)
            if count == limit:
                break
        return rows
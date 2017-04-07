from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
from jsontableschema import Table


# Module API

class Resource(object):
    """Data Resource representation.

    Arguments:
        descriptor (dict): VALID Data Resource descriptor
        base_path (str): base path to resolve local paths

    Descriptor updates:
        - dereferencing
        - applying defaults

    """

    # Public

    def __init__(self, descriptor, base_path=None):

        # Update descriptor
        descriptor = helpers.dereference_resource(descriptor, base_path)
        descriptor = helpers.apply_defaults_to_resource(descriptor)

        # Set attributes
        self.__descriptor = descriptor
        self.__base_path = base_path

    def descriptor(self):
        return self.__descriptor

    @property
    def type(self):
        """str: resource type:

        Resource types:
            - inline
            - local
            - remote
            - multipart-local
            - multipart-remote

        """
        data = descriptor.get('data')
        path = descriptor.get('path')
        # Inline
        if data is not None:
            return 'inline'
        # Local/Remote
        if len(path) == 1:
            if path[0].startswith('http'):
                return 'local'
            else:
                return 'remote'
        # Multipart Local/Remote
        if len(path) > 1:
            if path[0].startswith('http'):
                return 'multipart-local'
            else:
                return 'multipart-remote'

    def source(self):
        """any/str/str[0]: normalized data source

        Based on resource type:
            - inline -> data (any)
            - local/remote -> path[0] (str)
            - multipart-local/multipart-remote -> path (str[])

        Example:

        ```
        if resource.type == 'local':
            open(resource.source, mode='rb').read()
        elif resource.type == 'remote':
            requests.get(resource.source).text
        elif resource.type.startswith('multipart'):
            # use logic to handle list of chunks
        ```

        """
        if self.type == 'inline':
            return self.descriptor['data']
        if self.type in ['local', 'remote']:
            return self.descriptor['path'][0]
        if self.type in ['multipart-local', 'multipart-remote']:
            return self.descriptor['path']

    def table(self):
        pass

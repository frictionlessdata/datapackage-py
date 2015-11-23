from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from io import StringIO

import requests

from . import compat


class Registry(object):
    REGISTRY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'registry'
    )

    DEFAULT_CONFIG = {
        'backend': os.path.join(REGISTRY_PATH, 'registry.csv'),
    }

    def __init__(self, user_config=None):
        config = user_config or self.DEFAULT_CONFIG
        self._profiles = self._get_registry_at_endpoint(config['backend'])

    @property
    def profiles(self):
        return self._profiles

    def _get_registry_at_endpoint(self, endpoint):
        '''Return an array of objects from a CSV endpoint'''
        if os.path.isfile(endpoint):
            data = open(endpoint, 'r')
        else:
            resp = requests.get(endpoint)
            resp.raise_for_status()

            data = StringIO(resp.text)

        reader = compat.csv_dict_reader(data)

        return [o for o in reader]

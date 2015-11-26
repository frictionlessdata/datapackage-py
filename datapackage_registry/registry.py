from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
from io import StringIO

import requests

from . import compat


class Registry(object):
    DEFAULT_REGISTRY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'registry'
    )

    DEFAULT_CONFIG = {
        'backend': os.path.join(DEFAULT_REGISTRY_PATH, 'registry.csv'),
    }

    def __init__(self, user_config=None):
        config = user_config or self.DEFAULT_CONFIG
        if os.path.isfile(config['backend']):
            self.REGISTRY_PATH = os.path.dirname(config['backend'])
        self._registry = self._get_registry_at_endpoint(config['backend'])
        self._profiles = {}

    @property
    def available_profiles(self):
        '''Return the available profiles' metadata as a dict of dicts'''
        return self._registry

    def get(self, profile_id):
        '''Return the profile with the received ID as a dict

        If a local copy of the profile exists, it'll be returned. If not, it'll
        be downloaded from the web.
        '''
        if profile_id not in self._profiles:
            self._profiles[profile_id] = self._get_profile(profile_id)
        return self._profiles[profile_id]

    def _get_profile(self, profile_id):
        '''Return the profile with the received ID as a dict'''
        profile_metadata = self._registry.get(profile_id)
        if not profile_metadata:
            return

        relative_path = profile_metadata.get('relative_path')
        if relative_path and hasattr(self, 'REGISTRY_PATH'):
            path = os.path.join(self.REGISTRY_PATH, relative_path)
            if os.path.isfile(path):
                return json.load(open(path, 'r'))

        url = profile_metadata.get('schema')
        if url:
            resp = requests.get(url)
            return resp.json()

    def _get_registry_at_endpoint(self, endpoint):
        '''Return an array of objects from a CSV endpoint'''
        if os.path.isfile(endpoint):
            data = open(endpoint, 'r')
        else:
            resp = requests.get(endpoint)
            resp.raise_for_status()

            data = StringIO(resp.text)

        reader = compat.csv_dict_reader(data)

        return dict([(o['id'], o) for o in reader])

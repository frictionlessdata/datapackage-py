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
        self._profiles = self._get_registry_at_endpoint(config['backend'])
        self._profiles_cache = {}

    @property
    def profiles(self):
        '''Return the DataPackage Registry as an array of objects'''
        return self._profiles

    def get(self, profile_id):
        '''Return the profile with the received ID as a dict

        If a local copy of the profile exists, it'll be returned. If not, this
        method will download it from the web.
        '''
        if profile_id not in self._profiles_cache:
            self._profiles_cache[profile_id] = self._get_profile(profile_id)
        return self._profiles_cache[profile_id]

    def _get_profile(self, profile_id):
        '''Return the profile with the received ID as a dict'''
        profile_metadata = [profile for profile in self.profiles
                            if profile['id'] == profile_id]
        if not profile_metadata:
            return
        profile_metadata = profile_metadata[0]

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

        return [o for o in reader]

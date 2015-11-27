from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import json
from io import StringIO

import six
import requests

from . import compat
from .exceptions import DataPackageRegistryException


class Registry(object):
    DEFAULT_REGISTRY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'schemas',
        'registry.csv'
    )

    def __init__(self, registry_path_or_url=DEFAULT_REGISTRY_PATH):
        '''Allows interfacing with a dataprotocols schema registry

        This method raises DataPackageRegistryException if there were any
        errors.
        '''
        if os.path.isfile(registry_path_or_url):
            self._BASE_PATH = os.path.dirname(
                os.path.abspath(registry_path_or_url)
            )
        try:
            self._profiles = {}
            self._registry = self._get_registry(registry_path_or_url)
        except (IOError,
                ValueError,
                KeyError,
                requests.exceptions.RequestException) as e:
            six.raise_from(DataPackageRegistryException(e), e)

    @property
    def available_profiles(self):
        '''Return the available profiles' metadata as a dict of dicts'''
        return self._registry

    def get(self, profile_id):
        '''Return the profile with the received ID as a dict

        If a local copy of the profile exists, it'll be returned. If not, it'll
        be downloaded from the web. The results are cached, so any subsequent
        calls won't hit the filesystem or the web.

        This method raises DataPackageRegistryException if there were any
        errors.
        '''
        if profile_id not in self._profiles:
            try:
                self._profiles[profile_id] = self._get_profile(profile_id)
            except (IOError,
                    ValueError,
                    requests.exceptions.RequestException) as e:
                six.raise_from(DataPackageRegistryException(e), e)
        return self._profiles[profile_id]

    def _get_profile(self, profile_id):
        '''Return the profile with the received ID as a dict'''
        profile_metadata = self._registry.get(profile_id)
        if not profile_metadata:
            return

        path = self._get_absolute_path(profile_metadata.get('schema_path'))
        if path:
            if os.path.isfile(path):
                return json.load(open(path, 'r'))

        url = profile_metadata.get('schema')
        if url:
            resp = requests.get(url)
            return resp.json()

    def _get_registry(self, registry_path_or_url):
        '''Return a dict with objects mapped by their id from a CSV endpoint'''
        if os.path.isfile(registry_path_or_url):
            data = open(registry_path_or_url, 'r')
        else:
            res = requests.get(registry_path_or_url)
            res.raise_for_status()

            data = StringIO(res.text)

        reader = compat.csv_dict_reader(data)

        return dict([(o['id'], o) for o in reader])

    def _get_absolute_path(self, relative_path):
        '''Return the received relative_path joined with the base path

        It'll return None if something goes wrong.
        '''
        try:
            return os.path.join(self._BASE_PATH, relative_path)
        except:
            pass

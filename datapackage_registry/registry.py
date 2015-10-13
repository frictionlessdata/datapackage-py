from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from StringIO import StringIO

import csv
import requests


DEFAULT_CONFIG = {
  'backend': 'https://rawgit.com/dataprotocols/registry/master/registry.csv',
}


def _get_registry_at_endpoint(endpoint):
    '''Return an array of objects from an endpoint that is parsable as CSV'''
    resp = requests.get(endpoint)

    data = StringIO(resp.text)

    reader = csv.DictReader(data)

    return [o for o in reader]


def get_registry(user_config=None):
    '''Return the DataPackage Registry as an array of objects'''
    config = user_config or DEFAULT_CONFIG

    return _get_registry_at_endpoint(config['backend'])

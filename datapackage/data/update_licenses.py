#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import codecs

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen


OPENDEFINITION_LICENSES_URL = \
    'http://licenses.opendefinition.org/licenses/groups/all.json'


def load_licenses_aliases():
    dirname = os.path.split(os.path.realpath(__file__))[0]
    filename = os.path.join(dirname, 'licenses_aliases.json')
    with io.open(filename, 'r') as fh:
        aliases = json.load(fh)
    return aliases


def load_opendefinition_licenses(url=OPENDEFINITION_LICENSES_URL):
    fh = urlopen(url)
    reader = codecs.getreader('utf-8')
    licenses = json.load(reader(fh))
    return licenses


def generate_licenses_json():
    aliases = load_licenses_aliases()
    od_licenses = load_opendefinition_licenses()
    licenses = {}

    for _, details in od_licenses.items():
        if (details.get('domain_data') or details.get('domain_content') and
                details['url']):
            licenses[details['id']] = details['url']
            for alias in aliases.get(details['id'], []):
                licenses[alias] = details['url']

    return json.dumps(licenses,
                      sort_keys=True, indent=4, separators=(',', ': '))


def save_licenses_json():
    dirname = os.path.split(os.path.realpath(__file__))[0]
    filename = os.path.join(dirname, 'licenses.json')
    content = generate_licenses_json()
    with io.open(filename, 'w') as fh:
        fh.write(content)


if __name__ == '__main__':
    save_licenses_json()

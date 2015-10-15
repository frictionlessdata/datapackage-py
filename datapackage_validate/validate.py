from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

# from . import compat


def validate(raw, schema=None):
    '''
    `raw` is a json string
    '''
    # schema_id = schema or 'base'

    valid = True
    errors = []

    # check json is well formed
    if type(raw) == unicode:
        try:
            json.loads(raw)
        except ValueError as e:
            valid = False
            errors.append('Invalid JSON: {0}'.format(e))

    return valid, errors

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from nose.tools import (assert_true,
                        assert_false,
                        assert_equal,
                        assert_raises)

import datapackage_validate


class TestValidJsonString(object):

    def test_valid_json_string(self):
        '''validate() returns True with no error messages.'''
        json_str = '{"xyz":123}'
        valid, errors = datapackage_validate.validate(json_str)

        assert_true(valid)
        assert_false(errors)

    def test_invalid_json_string(self):
        '''validate() returns False, with expected error message.'''
        invalid_json_str = '{"xyz":123'
        valid, errors = datapackage_validate.validate(invalid_json_str)

        assert_false(valid)
        assert_true(errors)
        assert_true('Invalid JSON:' in errors[0])

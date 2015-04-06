# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .util import Specification, is_url, is_email
from . import compat


class Source(Specification):
    """
    Source object which can be added to a DataPackage object or a Resource
    object to represent where the data comes from.

    From the specification:
    Each source hash may have name, web and email fields.
    """

    SPECIFICATION = {'name': compat.str,
                     'web': compat.str,
                     'email': compat.str}

    @property
    def web(self):
        """
        Link to the source of the data on the web
        """
        return self['web']

    @web.setter
    def web(self, value):
        if not value:
            if 'web' in self:
                del self['web']
            return

        if not is_url(value):
            raise ValueError("not a url: {0}".format(value))

        self['web'] = value

    @property
    def email(self):
        """
        Email address to the source of the data (person, organisation etc.)
        """
        return self['email']

    @email.setter
    def email(self, value):
        if not value:
            if 'email' in self:
                del self['email']
            return

        if not is_email(value):
            raise ValueError("not an email address: {0}".format(value))

        self['email'] = value

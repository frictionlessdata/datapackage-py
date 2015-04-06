# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .util import Specification, is_url, is_email
from . import compat


class Person(Specification):
    """
    Person object which can be added to a DataPackage object, e.g. as
    maintainers, contributors or publishers. Person could in theory also
    be an organisation but is left here as a Person.

    From the specification:
    [A] hash which must have a "name" property and may optionally provide
    "email" and "web" properties.
    """

    SPECIFICATION = {'name': compat.str,
                     'web': compat.str,
                     'email': compat.str}
    REQUIRED = ('name',)

    @property
    def name(self):
        """
        Name of the person or organisation
        """
        return self['name']

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError('A person must have a name')
        self['name'] = compat.str(value)

    @property
    def web(self):
        """
        Link to the person's or organisation's website
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

        self['web'] = compat.str(value)

    @property
    def email(self):
        """
        Email address of the person or organisation.
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

        self['email'] = compat.str(value)

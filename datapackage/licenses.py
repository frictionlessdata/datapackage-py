# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .util import Specification, is_url, load_licenses
from . import compat


LICENSES = load_licenses()


class License(Specification):
    """
    License object which can be added to a DataPackage's license or licenses
    array or a Resource's licensese array.

    From the specification:
    "[E]ntry MUST be a hash with a type. The type SHOULD be an
    **Open Definition license** ID if an ID exists for the license.
    If another license name or identifier is used as type then the
    url property MUST link to the actual license text. The url
    property MAY be specified when used in combination with an
    **Open Definition license ID**.
    """

    SPECIFICATION = {'type': compat.str,
                     'url': compat.str}

    def __init__(self, *args, **kwargs):
        # We need to pick them out in a specific order to make sure that
        # the url is set when type is not an Open Definition license id
        self.url = kwargs.pop('url', None)
        self.type = kwargs.pop('type', None)
        super(License, self).__init__(*args, **kwargs)

    @property
    def type(self):
        """
        The type should be an **Open Definition license** ID but
        can be any string which then has to be combined with a
        link
        """
        return self['type']

    @type.setter
    def type(self, value):
        if not value:
            raise ValueError('License type is missing')

        value = value.upper()
        self['type'] = value

        license_url = LICENSES.get(value, None)
        if 'url' not in self and license_url is None:
            raise AttributeError(
                "url is required if type isn't {0}".format(
                    "an Open Definition license ID"))

    @property
    def url(self):
        """
        Link to the license text. This must be provided if the
        type is not an **Open Definition license** ID and should
        then link to the actual license text.
        """
        return self['url']

    @url.setter
    def url(self, value):
        if not value:
            if 'url' in self:
                if 'type' in self and self.type not in LICENSES:
                    raise AttributeError(
                        "url is required if type isn't {0}".format(
                            "an Open Definition license ID"))
                del self['url']
            return

        if not is_url(value):
            raise ValueError("not a url: {0}".format(value))
        self['url'] = value

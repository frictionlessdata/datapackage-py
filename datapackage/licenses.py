import sys
if sys.version_info[0] < 3:
    next = lambda x: x.next()
    bytes = str
    str = unicode

from .util import Specification, is_url, load_licenses
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

    SPECIFICATION = {'type': str,
                     'url': str}

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
            raise ValueError("not a url: {}".format(value))
        self['url'] = value


def get_licenses(descriptor):
    """MUST be an array. Each entry MUST be a hash with a type and a url
    property linking to the actual text. The type SHOULD be an Open
    Definition license ID if an ID exists for the license and
    otherwise may be the general license name or identifier.

    """
    descriptor_license = descriptor.get('license')
    descriptor_licenses = descriptor.get('licenses')
    if descriptor_license and descriptor_licenses:
        raise KeyError("datapackage has both license and licenses defined")
    elif descriptor_license:
        return [{
            "type": descriptor_license,
            "url": LICENSES.get(descriptor_license, None)
        }]
    elif descriptor_licenses:
        return descriptor_licenses
    else:
        return []


def set_licenses(descriptor, val):
    if 'license' in descriptor:
        del descriptor['license']
    for descriptor_license in val:
        if sorted(descriptor_license.keys()) != ["type", "url"]:
            raise ValueError(
                "license should only have keys for 'type' and 'url'")
        url = descriptor_license["url"]
        if url and not is_url(url):
            raise ValueError("not a url: {}".format(url))
    descriptor['licenses'] = val


def add_license(descriptor, license_type, url=None):
    """Adds a license to the list of licenses for the datapackage.

    :param string license_type: The name of the license, which
        should be an Open Definition license ID if an ID exists
        for the license and otherwise may be the general license
        name or identifier.
    :param string url: The URL corresponding to the license. If
        license_type is a standard Open Definition license, then
        the URL will try to be inferred automatically.

    """
    url = url or LICENSES.get(license_type, None)
    licenses = get_licenses(descriptor)
    licenses.append({"type": license_type, "url": url})
    set_licenses(descriptor, licenses)

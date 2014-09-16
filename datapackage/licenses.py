import sys
if sys.version_info[0] < 3:
    next = lambda x: x.next()
    bytes = str
    str = unicode

from .util import is_url, load_licenses
LICENSES = load_licenses()


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

import sys
import os
import json
import urllib
import re

if sys.version_info[0] < 3:
    import urlparse
    urllib.parse = urlparse
    urllib.request = urllib
    next = lambda x: x.next()
    bytes = str
    str = unicode


def verify_semantic_version(version):
    """Verify that semantic versioning (http://semver.org/) is being
    followed. In particular, the version should have a major version,
    minor version, and patch version, separated by periods.

    """
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(
            "version '{}' does not follow semantic versioning".format(version))
    return str(version)


def get_licenses():
    """Reads a dictionary of licenses, and their corresponding URLs, out
    of a JSON file."""
    # figure out the real directory name relative to this file, so we
    # can read in the licenses file
    dirname = os.path.split(os.path.realpath(__file__))[0]
    filename = os.path.join(dirname, "data", "licenses.json")
    with open(filename, "r") as fh:
        licenses = json.load(fh)
    return licenses


def is_local(path):
    """Checks whether a path is a local path, or a remote URL. This simple
    check just looks if there is a scheme or netloc associated with
    the path (and will therefore return False when the path uses the
    file: scheme)

    """
    parsed_results = urllib.parse.urlparse(path)
    return parsed_results.scheme == '' or parsed_results.netloc == ''


def is_url(path):
    """Checks whether a path is a valid http or https URL. This simple
    check just looks if the scheme is HTTP or HTTPS.

    """
    parsed_results = urllib.parse.urlparse(path)
    return parsed_results.scheme == 'http' or parsed_results.scheme == 'https'


def is_email(val):
    """Checks to see whether a string is a valid email address.  Email
    addresses can actually be complicated, so this just performs the
    minimal check that there is <something>@<something>.<something>

    """
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", val))

import sys
import os
import json
import urllib
import re
from collections import namedtuple

if sys.version_info[0] < 3:
    import urlparse
    urllib.parse = urlparse
    urllib.request = urllib
    next = lambda x: x.next()
    bytes = str
    str = unicode


# This is a named tuple for representing semantic versions (see
# http://semver.org/). Semantic versions look like this:
#
#    major.minor.patch-prerelease+metadata
#
# where the -prerelease and +metadata are optional. The major, minor,
# and patch versions should all be integers; the prerelease and
# metadata versions should be alphanumeric (plus hyphens and periods
# are ok).
SemanticVersion = namedtuple(
    "SemanticVersion",
    ["major", "minor", "patch", "prerelease", "metadata"])


# For semantic versioning, the pre-release and metadata should only be
# alphanumeric plus hyphens and periods
valid_version_regex = re.compile(r"^[0-9A-Za-z-\.]+$")


def parse_version(version):
    """Parse a version string according to semantic versioning.

    """
    # make sure there are the right number of parts
    parts = version.split('.', 2)
    if len(parts) != 3:
        raise ValueError(
            "version '{}' does not follow semantic versioning".format(version))
    major, minor, patch = parts

    # check that the major version is valid
    try:
        major = int(major)
    except ValueError:
        raise ValueError("major version is not an integer: {}".format(major))

    # check that the minor version is valid
    try:
        minor = int(minor)
    except ValueError:
        raise ValueError("minor version is not an integer: {}".format(major))

    # check for metadata
    if "+" in patch:
        patch, metadata = patch.split("+", 1)
    else:
        metadata = None

    # check for pre-release
    if "-" in patch:
        patch, prerelease = patch.split("-", 1)
    else:
        prerelease = None

    # check that the patch version is valid
    try:
        patch = int(patch)
    except ValueError:
        raise ValueError("patch version is not an integer: {}".format(patch))

    # check that prerelease is valid
    if prerelease:
        match = valid_version_regex.match(prerelease)
        if not match:
            raise ValueError(
                "invalid pre-release version: {}".format(prerelease))

    # check that metadata is valid
    if metadata:
        match = valid_version_regex.match(metadata)
        if not match:
            raise ValueError(
                "invalid metadata: {}".format(metadata))

    version = SemanticVersion(major, minor, patch, prerelease, metadata)
    return version


def format_version(version):
    """Formats a semantic version given by a tuple with:

    (major, minor, patch, prerelease, metadata)

    where prerelease and metadata may be None.

    """
    major, minor, patch, prerelease, metadata = version
    version = u".".join([str(major), str(minor), str(patch)])
    if prerelease:
        version = u"{}-{}".format(version, prerelease)
    if metadata:
        version = u"{}+{}".format(version, metadata)
    return version


def verify_version(version):
    """Verifies that a version string follows semantic versioning. If it
    passes, this will just return the version string; if it fails, an
    exception will be raised.

    """
    return format_version(parse_version(version))


def load_licenses():
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


def is_mimetype(val):
    """Checks to see whether a string is a valid mimetype. This is a very
    basic check that just looks for <something>/<something>.

    """
    return bool(re.match(r"[^/]+/[^/]+", val))

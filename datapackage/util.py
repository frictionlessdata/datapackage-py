import sys
import os
import json

if sys.version_info[0] < 3:
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
    # figure out the real directory name relative to this file, so we
    # can read in the licenses file
    dirname = os.path.split(os.path.realpath(__file__))[0]
    filename = os.path.join(dirname, "data", "licenses.json")
    with open(filename, "r") as fh:
        licenses = json.load(fh)
    return licenses

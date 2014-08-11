import sys
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

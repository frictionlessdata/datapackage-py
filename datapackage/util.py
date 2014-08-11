import sys
if sys.version_info[0] < 3:
    next = lambda x: x.next()
    bytes = str
    str = unicode


def verify_semantic_version(val):
    parts = val.split('.')
    if len(parts) != 3:
        raise ValueError(
            "version '{}' does not follow semantic versioning".format(val))
    return str(val)

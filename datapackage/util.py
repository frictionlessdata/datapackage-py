# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import io
import json
import re
from collections import namedtuple
from . import compat


class Specification(dict):

    # Allowed keys in the specification object and their types.
    # These are the currently allowed data package keys
    # and should preferably be parsed from a data package
    # specification representation (instead of being hardcoded).
    SPECIFICATION = {}
    REQUIRED = ()
    EXTENDABLE = False
    SERIALIZE_EXCLUDES = ()

    def __init__(self, *args, **kwargs):
        """
        Initialize a new Specification object.

        Keyword arguments can set attributes/values on instance creation
        """

        # Check if required fields are missing
        missing_fields = self.ensure_required(kwargs)
        if missing_fields:
            raise ValueError('Required fields for {0} missing: {1}'.format(
                self.__class__.__name__,
                ' AND '.join(missing_fields)))

        for (key, value) in kwargs.items():
            self.__setattr__(key, value)

    def as_dict(self):
        """Output a dict of the specification."""
        return dict((k, v) for k, v in self.items() if
                    k not in self.SERIALIZE_EXCLUDES)

    def as_json(self):
        """Output a JSON object of the specification."""
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=4)

    def __getattr__(self, attribute):
        # If the attribute has been defined as a real attribute
        # e.g. as a property, we use the object getter instead of
        # our own
        if hasattr(self.__class__, attribute):
            return object.__getattribute__(self, attribute)

        if attribute in self.SPECIFICATION.keys():
            return dict.get(self, attribute, None)
        else:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(
                self.__class__.__name__, attribute))

    def __setattr__(self, attribute, value):
        # If the attribute has been defined as a real attribute
        # e.g. as a property with its own setter, we use the object
        # setter instead of our custom one
        if hasattr(self.__class__, attribute):
            object.__setattr__(self, attribute, value)
            return

        # The specification does not expect any value for a key to be
        # None (null) so we skip it instead of adding a None value
        if value is None:
            # If the attribute exists we delete it when the value is None
            if dict.__contains__(self, attribute):
                dict.__delitem__(self, attribute)
            return
        # Attribute must exist in the specification keys
        if attribute in self.SPECIFICATION.keys():
            spec_type = self.SPECIFICATION[attribute]
            # If spec_type is None we don't do any validation of type
            if spec_type is not None:
                # To accommodate for multiple types we cast non-tuples into
                # a tuple to make later processing easier
                if type(spec_type) != tuple:
                    spec_type = (spec_type,)
                if not isinstance(value, spec_type):
                    raise TypeError(
                        "Attribute '{0}' ({1}) should be {2}".format(
                            attribute, type(value),
                            ' or '.join([compat.str(s) for s in spec_type])))
        elif not self.EXTENDABLE:
            raise AttributeError(
                "Attribute '{0}' is not allowed in a '{1}' object".format(
                    attribute, self.__class__.__name__))

        dict.__setitem__(self, attribute, value)

    def process_object_array(self, array, object_class):
        """
        Method for processing an array of dict object which should be cast
        into a specific class (array of that class' instances). The dict
        objects could already be of that class and if so they are left intact.

        :param array: List to process
        :param object_class: Class to cast objects into
        """
        # Check if array is a list
        if type(array) != list:
            raise TypeError(
                '{0} must be a list not {1}'.format(
                    object_class.__name__, type(array)))

        # We loop through the list and create object_class instances from
        # dicts or throw errors if the type is invalid
        modified_array = []
        for value in array:
            if isinstance(value, object_class):
                # We don't need to do anything if it already
                # is of the correct class
                pass
            elif type(value) == dict:
                # We turn the single_value into kwargs and pass it into
                # the object_class constructor
                value = object_class(**value)
            else:
                raise TypeError('{0} type {1} is invalid'.format(
                    object_class.__name__, type(value)))
            modified_array.append(value)

        return modified_array

    def ensure_required(self, kwargs):

        """Ensure all required fields are present.

        Returns:
            * a list of field names that are required and missing

        """

        missing_fields = []
        for field in self.REQUIRED:
            if isinstance(field, (list, tuple)):
                found = False
                for field_choice in field:
                    if field_choice in kwargs:
                        found = True
                if not found:
                    missing_fields.append(' or '.join(field))
            else:
                if field not in kwargs:
                    missing_fields.append(field)

        return missing_fields

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
            "version '{0}' does not follow semantic versioning".format(version)
        )
    major, minor, patch = parts

    # check that the major version is valid
    try:
        major = int(major)
    except ValueError:
        raise ValueError("major version is not an integer: {0}".format(major))

    # check that the minor version is valid
    try:
        minor = int(minor)
    except ValueError:
        raise ValueError("minor version is not an integer: {0}".format(major))

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
        raise ValueError("patch version is not an integer: {0}".format(patch))

    # check that prerelease is valid
    if prerelease:
        match = valid_version_regex.match(prerelease)
        if not match:
            raise ValueError(
                "invalid pre-release version: {0}".format(prerelease))

    # check that metadata is valid
    if metadata:
        match = valid_version_regex.match(metadata)
        if not match:
            raise ValueError(
                "invalid metadata: {0}".format(metadata))

    version = SemanticVersion(major, minor, patch, prerelease, metadata)
    return version


def format_version(version):
    """Formats a semantic version given by a tuple with:

    (major, minor, patch, prerelease, metadata)

    where prerelease and metadata may be None.

    """
    major, minor, patch, prerelease, metadata = version
    version = "{0}.{1}.{2}".format(major, minor, patch)
    if prerelease:
        version = "{0}-{1}".format(version, prerelease)
    if metadata:
        version = "{0}+{1}".format(version, metadata)
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
    with io.open(filename, "r") as fh:
        licenses = json.load(fh)
    return licenses


def is_local(path):
    """Checks whether a path is a local path, or a remote URL. This simple
    check just looks if there is a scheme or netloc associated with
    the path (and will therefore return False when the path uses the
    file: scheme)

    """
    parsed_results = compat.parse.urlparse(path)
    return parsed_results.scheme == '' or parsed_results.netloc == ''


def is_url(path):
    """Checks whether a path is a valid http or https URL. This simple
    check just looks if the scheme is HTTP or HTTPS.

    """
    parsed_results = compat.parse.urlparse(path)
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


def get_size_from_url(url):
    site = compat.urlopen(url)
    meta = site.info()
    size = int(meta.getheaders("Content-Length")[0])
    return size

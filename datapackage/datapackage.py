# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# datapackage.py - Load and manage data packages defined by dataprotocols.org
# Copyright (C) 2013 Tryggvi Björgvinsson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import itertools
import os
import datetime
import time
import base64
import re
import io
import warnings
from .resource import Resource
from .schema import Schema
from .sources import Source
from .licenses import License, LICENSES
from .persons import Person
from .util import (Specification, verify_version, parse_version,
                   format_version, is_local, is_url)
from . import compat


class DataPackage(Specification):
    """
    Package for loading and managing a data package as defined by:
    http://www.dataprotocols.org/en/latest/data-packages.html
    """

    DATAPACKAGE_VERSION = "1.0-beta.10"
    EXTENDABLE = True
    SPECIFICATION = {'name': compat.str,
                     'resources': list,
                     'license': compat.str,
                     'licenses': list,
                     'datapackage_version': compat.str,
                     'title': compat.str,
                     'description': compat.str,
                     'homepage': compat.str,
                     'version': compat.str,
                     'sources': list,
                     'keywords': list,
                     'image': compat.str,
                     'maintainers': list,
                     'contributors': list,
                     'publishers': list,
                     'base': compat.basestring,
                     'dataDependencies': dict}
    REQUIRED = ('name',)
    RESOURCE_CLASS = Resource

    FIELD_PARSERS = {
        'number': float,
        'integer': int,
        'date': lambda x:
            datetime.datetime.strptime(x, '%Y-%m-%d').date(),
        'time': lambda x: time.strptime(x, '%H:%M'),
        'datetime': lambda x:
            datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%Z'),
        'boolean': bool,
        'binary': base64.b64decode,
        'object': json.loads,
        'json': json.loads,
        'geojson': json.loads,
        'array': list,
        }

    def __init__(self, *args, **kwargs):
        """
        Create or load an existing DataPackage.

        :param basestring uri: Optional argument. Provide URI or file path
            to a data package to be loaded. ``datapackage.json`` should exist
            under this URI. If not provided keyword arguments can be used to
            create a new DataPackage
        """

        # URI to an existing Data Package can be provided as an argument
        # If that's the case then we start off by loading that data package
        if not args:
            super(DataPackage, self).__init__(*args, **kwargs)
        elif len(args) == 1:
            self.base = args[0]
            descriptor = self.get_descriptor()
            super(DataPackage, self).__init__(**descriptor)
        else:
            raise TypeError('DataPackage takes 0 or 1 arguments')

    def _field_parser(self, field):
        """
        Return a type casting function (field parser) based on the data
        package field types. This returns the default type/functions for
        the types except when the field type is either data or datetime.
        In that case it returns the correctly formatted string (YYYY/MM/DD
        is even supported). Also if the field type is geopoint it returns
        the a function that parses the value as as
        {'lat': latitude_as_float, 'lon': longitude_as_float}
        """

        # If a format is provided with the field we need a different way
        # to cast it as datetime
        if (field['type'] == 'date' or field['type'] == 'datetime') \
                and 'format' in field:

            # Get the format into its own variable, we need to make some
            # replacements
            format_string = field['format']
            # Order of the replacements is important since month and minutes
            # can be denoted in a similar fashion
            replacement_order = [('hh', '%m'), (':mm', ':%M'), ('ss', '%S'),
                                 ('yyyy', '%Y'), ('yy', '%y'), ('mm', '%m'),
                                 ('dd', '%d')]

            # For each replacement we substitute (and ignore the case)
            for (old, new) in replacement_order:
                format_string = re.sub("(?i)%s" % old, new, format_string)

            # Return the parser (here's a difference between date and datetime
            if field['type'] == 'datetime':
                return lambda x: datetime.datetime.strptime(x, format_string)
            else:
                return lambda x: \
                    datetime.datetime.strptime(x, format_string).date()

        # If type is geopoint we need to create a parser that can parse three
        # different formats into one dictionary
        if field['type'] == 'geopoint':
            def parse_geopoint(value):
                # Try to load it as json ( if it an dictionary object or array)
                try:
                    parsed = json.loads(value)
                    if type(parsed) == list:
                        # Geopoint coded as [123.4, 567.8]
                        return {'lat': parsed[0], 'lon': parsed[1]}
                    else:
                        # Geopoint coded as {'lat':123.4, 'lon':567.8}
                        return parsed
                except:
                    # Geopoint probably coded as "123.4, 567.8"
                    geotuple = value.split(',')
                    return {
                        'lat': float(geotuple[0]),
                        'lon': float(geotuple[1])
                    }

            # Return the parser
            return parse_geopoint

        # If none of the edge cases we use the default field parsers and fall
        # back on unicode type if no parser is found
        return self.FIELD_PARSERS.get(field['type'], compat.str)

    def open_resource(self, path):
        # If base hasn't been set we use the current directory as the base
        if self.base:
            base = self.base
        else:
            base = os.path.curdir
        # use os.path.join if the path is local, otherwise use urljoin
        # -- we don't want to just use os.path.join because otherwise
        # on Windows it will try to create URLs with backslashes
        if is_local(base):
            resource_path = os.path.join(base, path)
            return io.open(resource_path)
        else:
            resource_path = compat.parse.urljoin(base, path)
            return compat.urlopen(resource_path)

    @property
    def name(self):
        """The name of the dataset as described by its descriptor. This is a
        required property, described by the datapackage protocol as
        follows:

        short url-usable (and preferably human-readable) name of the
        package. This MUST be lower-case and contain only alphanumeric
        characters along with ".", "_" or "-" characters. It will
        function as a unique identifier and therefore SHOULD be unique
        in relation to any registry in which this package will be
        deposited (and preferably globally unique).

        The name SHOULD be invariant, meaning that it SHOULD NOT
        change when a data package is updated, unless the new package
        version should be considered a distinct package, e.g. due to
        significant changes in structure or interpretation. Version
        distinction SHOULD be left to the version field. As a
        corollary, the name also SHOULD NOT include an indication of
        time range covered.

        """
        name = self.get('name')
        if not name:
            raise KeyError("datapackage does not have a name")
        return name

    @name.setter
    def name(self, val):
        if not val:
            raise ValueError("datapackage name must be non-empty")

        self['name'] = val

    @property
    def license(self):
        """
        MUST be a string and its value SHOULD be an Open Definition license
        ID (preferably one that is Open Definition approved).
        """
        return self['license']

    @license.setter
    def license(self, value):
        if value not in LICENSES:
            raise ValueError(
                "License string must be an Open Definition License ID")
        self['license'] = value
        # If there were licenses already we remove them
        if 'licenses' in self:
            del self['licenses']

    @property
    def licenses(self):
        """MUST be an array. Each entry MUST be a hash with a type and a url
        property linking to the actual text. The type SHOULD be an
        Open Definition license ID if an ID exists for the license and
        otherwise may be the general license name or identifier.

        """
        return self.get('license', self['licenses'])

    @licenses.setter
    def licenses(self, value):
        if value is None:
            raise ValueError('Data package must have a license')

        if type(value) == list:
            # If there was a license already we remove it
            if 'license' in self:
                del self['license']
            self['licenses'] = self.process_object_array(value, License)
        else:
            if value not in LICENSES:
                raise ValueError(
                    "License string must be an Open Definition License ID")
            self['license'] = value

    def add_license(self, license_type, url=None):
        """Adds a license to the list of licenses for the datapackage.

        :param string license_type: The name of the license, which
            should be an Open Definition license ID if an ID exists
            for the license and otherwise may be the general license
            name or identifier.
        :param string url: The URL corresponding to the license. If
            license_type is a standard Open Definition license, then
            the URL will try to be inferred automatically.

        """
        # Create a new License object and add it to a list (or create a
        # new list if none exists). Depending on the resulting amount of
        # licenses key 'license' or 'licenses' will be used.
        added_license = License(type=license_type, url=url)
        if 'license' in self:
            # If license is present that's just a string but licenses are
            # a list of License objects so we need to convert it and delete
            # the license property since we cannot have both license and
            # licenses
            self.licenses = [License(type=self['license']), added_license]
            del self['license']
        elif 'licenses' in self:
            self.licenses.append(added_license)
        else:
            # No licenses added previously (should not happen since
            # licenses are required but we still implement this logic)
            if license_type in LICENSES:
                self['license'] = license_type
            else:
                self['licenses'] = [added_license]

    @property
    def datapackage_version(self):
        """The version of the data package specification this datapackage.json
        conforms to. It should follow the Semantic Versioning
        requirements (http://semver.org/).

        """
        return self.get('datapackage_version', self.DATAPACKAGE_VERSION)

    @datapackage_version.setter
    def datapackage_version(self, value):
        if not value:
            raise ValueError('datapackage_version is required')

        if value == self.DATAPACKAGE_VERSION:
            return

        warnings.warn(
            "DataPackage currently does not support multiple versions")

        self['datapackage_version'] = verify_version(value)

    @property
    def title(self):
        """
        The title of the dataset as described by its descriptor.
        """
        return self.get('title', None)

    @title.setter
    def title(self, value):
        if not value:
            if 'title' in self:
                del self['title']
            return

        self['title'] = compat.str(value)

    @property
    def description(self):
        """
        The description of the dataset as described by its descriptor.
        """

        return self.get('description', None)

    @description.setter
    def description(self, value):
        if not value:
            if 'description' in self:
                del self['description']
            return

        self['description'] = compat.str(value)

    @property
    def homepage(self):
        """
        URL string for the data packages web site
        """
        return self.get('homepage', None)

    @homepage.setter
    def homepage(self, value):
        if not value:
            if 'homepage' in self:
                del self['homepage']
            return

        if not is_url(value):
            raise ValueError("not a URL: {0}".format(value))

        self['homepage'] = compat.str(value)

    @property
    def version(self):
        """A version string identifying the version of the package. It should
        conform to the Semantic Versioning requirements
        (http://semver.org/).

        Defaults to 0.0.1 if not specified.

        """
        return self.get('version', '0.0.1')

    @version.setter
    def version(self, val):
        self['version'] = verify_version(val)

    def bump_major_version(self, keep_metadata=False):
        """Increases the major version by one, e.g. 1.0.0 --> 2.0.0

        Note that this sets the minor and patch versions to zero, and
        erases the prerelease and metadata information (unless
        `keep_metadata` is True, in which case the metadata will be
        preserved).

        """
        version = parse_version(self.version)
        major = version[0]
        if keep_metadata:
            metadata = version[-1]
        else:
            metadata = None
        new_version = format_version((major + 1, 0, 0, None, metadata))
        self.version = new_version

    def bump_minor_version(self, keep_metadata=False):
        """Increases the minor version by one, e.g. 1.0.0 --> 1.1.0

        Note that this sets the patch version to zero, and erases the
        prerelease and metadata information (unless `keep_metadata` is
        True, in which case the metadata will be preserved).

        """
        version = parse_version(self.version)
        major, minor = version[:2]
        if keep_metadata:
            metadata = version[-1]
        else:
            metadata = None
        new_version = format_version((major, minor + 1, 0, None, metadata))
        self.version = new_version

    def bump_patch_version(self, keep_metadata=False):
        """Increases the patch version by one, e.g. 1.0.0 --> 1.0.1

        Note that this erases the prerelease and metadata information
        (unless `keep_metadata` is True, in which case the metadata
        will be preserved).

        """
        version = parse_version(self.version)
        major, minor, patch = version[:3]
        if keep_metadata:
            metadata = version[-1]
        else:
            metadata = None
        new_version = format_version((major, minor, patch + 1, None, metadata))
        self.version = new_version

    @property
    def sources(self):
        """An array of source hashes. Each source hash may have name, web and
        email fields.

        Defaults to an empty list.

        """
        return self.get('sources', None)

    @sources.setter
    def sources(self, value):
        if not value:
            if 'sources' in self:
                del self['sources']
            return

        self['sources'] = self.process_object_array(value, Source)

    def add_source(self, name, web=None, email=None):
        """Adds a source to the list of sources for this datapackage.

        :param string name: The human-readable name of the source.
        :param string web: A URL pointing to the source.
        :param string email: An email address for the contact of the
            source.

        """
        # Create a new Source object and add it to a list (or create a
        # new list if none exists
        added_source = Source(name=name, web=web, email=email)
        if self.sources:
            self.sources.append(added_source)
        else:
            self.sources = [added_source]

    @property
    def keywords(self):
        """An array of string keywords to assist users searching for the
        package in catalogs.
        """
        return self.get('keywords', None)

    @keywords.setter
    def keywords(self, value):
        if not value:
            if 'keywords' in self:
                del self['keywords']
            return

        self['keywords'] = [compat.str(x) for x in value]

    @property
    def image(self):
        """A link to an image to use for this data package.
        """
        return self.get('image', None)

    @image.setter
    def image(self, value):
        if not value:
            if 'image' in self:
                del self['image']
            return

        self['image'] = compat.str(value)

    @property
    def maintainers(self):
        """
        List of maintainers as a Person object

        From specification:
        Array of maintainers of the package. Each maintainer is a hash
        which must have a "name" property and may optionally provide
        "email" and "web" properties.
        """
        return self.get('maintainers', None)

    @maintainers.setter
    def maintainers(self, value):
        if not value:
            if 'maintainers' in self:
                del self['maintainers']
            return

        self['maintainers'] = self.process_object_array(value, Person)

    @property
    def contributors(self):
        """
        List of contributors as a Person object

        From specification:
        Array of hashes each containing the details of a contributor.
        Must contain a "name" property and MAY contain an email and web
        property. By convention, the first contributor is the original
        author of the package.
        """
        return self.get('contributors', None)

    @contributors.setter
    def contributors(self, value):
        if not value:
            if 'contributors' in self:
                del self['contributors']
            return

        self['contributors'] = self.process_object_array(value, Person)

    @property
    def publisher(self):
        """
        List of publishers as a Person object which behaves just like
        ``contributors``.
        """
        return self.get('publisher', None)

    @publisher.setter
    def publisher(self, value):
        if not value:
            if 'publisher' in self:
                del self['publisher']
            return

        self['publisher'] = self.process_object_array(value, Person)

    @property
    def data(self):
        """
        An iterator that returns dictionary representation of the rows in
        all resources.
        """

        # Get all of the generators for the resources
        data_generators = [self.get_data(k) for k in self.resources]
        return itertools.chain.from_iterable(data_generators)

    def get_descriptor(self):
        """
        Get the descriptor for the data package (as defined by the standard)
        as a dictionary. This uses the URI provided by the constructor and
        performs a join with the descriptor URN. This follows the join rules
        of urlparse.urljoin which means for URLs that if the URI does
        not end with a slash the last piece of the URI will be replaced with
        the descriptor URN.
        """
        descriptor = self.open_resource('datapackage.json')

        # Load the descriptor json contents
        str_descriptor = descriptor.read()
        json_descriptor = json.loads(str_descriptor)

        # Return the descriptor json contents (as the dict json.load returns
        return json_descriptor

    @property
    def resources(self):
        """
        List of Resource instances representing the contents of the package

        From the specification:
        [A] JSON array of hashes that describe the contents of the package.
        """
        return self['resources']

    @resources.setter
    def resources(self, value):
        if not value:
            raise ValueError("resources is a required field")

        # Check if array is a list
        if type(value) != list:
            raise TypeError(
                '{0} must be a list not {1}'.format(
                    self.RESOURCE_CLASS.__name__, type(value)))

        # We loop through the list and create Resource objects from dicts
        # or throw errors if the type is invalid
        modified_array = []
        for single_value in value:
            if isinstance(single_value, self.RESOURCE_CLASS):
                # We don't need to do anything if it already
                # is of the correct class
                pass
            elif type(single_value) == dict:
                # We turn the single_value into kwargs and pass it into
                # the License constructor
                base = os.path.curdir if 'base' not in self else self.base
                single_value = self.RESOURCE_CLASS(datapackage_uri=base,
                                                   **single_value)
            else:
                raise TypeError('{0} type {1} is invalid'.format(
                    self.RESOURCE_CLASS.__name__, type(single_value)))
            modified_array.append(single_value)

        self['resources'] = modified_array

    def get_resources(self):
        """
        Get the data package's resources as a dictionary. The key for each
        resource is the value of its name attribute. If no name is provided
        then the key is an empty string. This means that resources can be
        overwritten if they have the same (or no name).
        """

        # Initialise the empty dictionary
        resources = {}
        # Loop through the resources
        for resource in self['resources']:
            # Create a resource dictionary
            rsource = {
                # Location is url path or None (in that order)
                'location': resource.get('url', resource.get('path', None)),
                # The encoding of the file - defaults to utf-8
                'encoding': resource.get('encoding', 'utf-8'),
                # Fields are found in schema.fields
                'fields': resource.get('schema', Schema()).get('fields', [])
            }
            # Add the resource to the resource dictionary collection
            resources[resource.get('name', resource.get('id', ''))] = rsource

        # Return the resource collection
        return resources

    def get_data(self, resource):
        """
        Generator that yields the data for a given resource.
        """
        # Open the resource location
        resource_path = None
        for location_type in ('url', 'path'):
            if location_type in resource:
                resource_path = resource[location_type]
                break
        if resource_path is None:
            raise NotImplementedError(
                'Datapackage currently only supports resource url and path')

        resource_file = self.open_resource(resource_path)
        resource_file = (line.decode(resource.get('encoding', 'utf-8'))
                         for line in resource_file)
        # We assume CSV so we create the csv file
        reader = compat.csv_reader(resource_file)
        # Throw away the first line (headers)
        next(reader)
        # For each row we yield it as a dictionary where keys are the field
        # names and the value the value in that row
        for row_idx, row in enumerate(reader):
            # Each row will be returned as a dictionary where the keys are
            # the field id
            row_dict = {}
            # Loop over fields in the schema and parse the values
            for field_idx, field in enumerate(resource.schema['fields']):
                # Again, id is an old deprecated word from the standard and
                # we use the name (but support the old id).
                field_name = field.get('name', field.get('id', ''))

                # Decode the field value
                value = row[field_idx]

                # We wrap this in a try clause so that we can give error
                # messages about specific fields in a row
                try:
                    row_dict[field_name] = self._field_parser(field)(value)
                except:
                    msg = 'Field "{field}" in row {row} could not be parsed.'
                    raise ValueError(msg.format(field=field_name, row=row_idx))

            yield row_dict

    def as_dict(self):
        """Override base to deal with resources."""
        _resources = [dict((k, v) for k, v in r.items() if
                           k not in r.SERIALIZE_EXCLUDES)
                      for r in self.resources]
        as_dict = super(DataPackage, self).as_dict()
        as_dict['resources'] = _resources
        return as_dict

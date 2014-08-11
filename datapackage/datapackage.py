# -*- coding: utf-8 -*-

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

import urllib
import io
import csv
import json
import itertools
import os
import datetime, time
import base64
import re
import sys
if sys.version_info[0] < 3:
    import urlparse
    urllib.parse = urlparse
    urllib.request = urllib
    next = lambda x: x.next()
    bytes = str
    str = unicode
else:
    import urllib.request


class DataPackage(object):
    """
    Package for loading and managing a data package as defined by:
    http://www.dataprotocols.org/en/latest/data-packages.html
    """

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
                    return {'lat': float(geotuple[0]), 'lon': float(geotuple[1])}

            # Return the parser
            return parse_geopoint

        # If none of the edge cases we use the default field parsers and fall
        # back on unicode type if no parser is found
        return self.FIELD_PARSERS.get(field['type'], str)

    def __init__(self, uri, opener=None):
        """
        Construct a DataPackage.

        :param basestring uri: URI or file path to the data package.
            ``datapackage.json`` should exist under this URI.
        :param function opener: optional function instead of ``urllib.urlopen``
            to read data; e.g. ``opener=zf.open`` where ``zf = ZipFS('a.zip')``
        :type opener: function
        """
        self.opener = opener or urllib.request.urlopen
        # Bind the URI to this instance
        self.uri = uri
        # Load the descriptor as a dictionary into a variable
        self.descriptor = self.get_descriptor()
        # Load the resources as a dictionary into a variable
        self.resources = self.get_resources()

    def open_resource(self, path):
        # use os.path.join if the path is local, otherwise use urljoin
        # -- we don't want to just use os.path.join because otherwise
        # on Windows it will try to create URLs with backslashes
        if self._package_is_local():
            return self.opener(os.path.join(self.uri, path))
        else:
            return self.opener(urllib.parse.urljoin(self.uri, path))

    @property
    def name(self):
        """
        The name of the dataset as described by its descriptor.
        Default is an empty string if no name is present
        """

        return self.descriptor.get('name', u'')

    @property
    def title(self):
        """
        The title of the dataset as described by its descriptor.
        Default is an empty string if no title is present
        """

        return self.descriptor.get('title', u'')

    @property
    def description(self):
        """
        The descriptor of the dataset as described by its descriptor.
        Default is an empty string if no description is present
        """

        return self.descriptor.get('description', u'')

    @property
    def data(self):
        """
        An iterator that returns dictionary representation of the rows in
        all resources.
        """

        # Get all of the generators for the resources
        data_generators = [self.get_data(k) for k in self.resources.keys()]
        return itertools.chain.from_iterable(data_generators)

    def _package_is_local(self):
        """
        Checks to see if the data package is located on the local file system.
        This simple check just looks if there is a scheme or netloc associated
        with the data package URI (and will therefore return False when the
        URI uses the file: scheme)
        """

        parsed_results = urllib.parse.urlparse(self.uri)
        return parsed_results.scheme == '' or parsed_results.netloc == ''

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
        str_descriptor = descriptor.read().decode()
        json_descriptor = json.loads(str_descriptor)

        # Return the descriptor json contents (as the dict json.load returns
        return json_descriptor

    def get_resources(self):
        """
        Get the data package's resources as a dictionary. The key for each
        resource is the value of its name attribute. If no name is provided then
        the key is an empty string. This means that resources can be
        overwritten if they have the same (or no name).
        """

        # Initialise the empty dictionary
        sources = {}
        # Loop through the resources
        for resource in self.descriptor['resources']:
            # Create a resource dictionary
            source = {'location':
                          # Location is url path or None (in that order)
                          resource.get('url', resource.get('path', None)),
                      'encoding':
                        # The encoding of the file - defaults to utf-8
                          resource.get('encoding', 'utf-8'),
                      'fields':
                          # Fields are found in schema.fields
                          resource.get('schema', {}).get('fields', [])
                      }
            # Add the resource to the resource dictionary collection
            sources[resource.get('name', resource.get('id', u''))] = source

        # Return the resource collection
        return sources

    def get_data(self, name='', id=''):
        """
        Generator that yields the data for a given resource.
        The resource defaults to a resource identified by the empty string
        (no name attribute in descriptor)
        """
        # We support both name and id (id is an old deprecated field in the
        # data package standard). If user has used id and not name we assign
        # the id to the name.
        if not name and id:
            name = id

        # Check if the id can be found in the resources or throw a KeyError
        if name not in self.resources:
            raise KeyError("Source not found")

        # Get the resource dictionary representation
        resource_dict = self.resources[name]
        # Open the resource location
        resource_file = self.open_resource(resource_dict['location'])
        resource_file = (line.decode(resource_dict.get('encoding'))
                         for line in resource_file)
        # We assume CSV so we create the csv file
        reader = csv.reader(resource_file)
        # Throw away the first line (headers)
        next(reader)
        # For each row we yield it as a dictionary where keys are the field
        # names and the value the value in that row
        for row_idx, row in enumerate(reader):
            # Each row will be returned as a dictionary where the keys are
            # the field id
            row_dict = {}
            # Loop over fields in the schema and parse the values
            for field_idx, field in enumerate(resource_dict['fields']):
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
                    msg = u'Field "{field}" in row {row} could not be parsed.'
                    raise ValueError(msg.format(field=field_name, row=row_idx))

            yield row_dict

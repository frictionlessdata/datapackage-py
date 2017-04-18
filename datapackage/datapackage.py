from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import json
import copy
import tempfile
import shutil
import zipfile
import six
import requests
import warnings
import jsonpointer
from .resource import Resource
from .profile import Profile
from . import exceptions
from . import helpers
from . import config


class DataPackage(object):
    """"Class for loading, validating and working with a Data Package.

    Args:
        descriptor (dict, str or file-like object, optional): The contents of the
            `datapackage.json` file. It can be a ``dict`` with its contents,
            a ``string`` with the local path for the file or its URL, or a
            file-like object. It also can point to a `ZIP` file with one and
            only one `datapackage.json` (it can be in a subfolder). If
            you're passing a ``dict``, it's a good practice to also set the
            ``default_base_path`` parameter to the absolute `datapackage.json`
            path.
        schema (dict or str, optional): The schema to be used to validate this
            data package. It can be a ``dict`` with the schema's contents or a
            ``str``. The string can contain the schema's ID if it's in the
            registry, a local path, or an URL.
        default_base_path (str, optional): The default path to be used to load
            resources located on the local disk that don't define a base path
            themselves. This will usually be the path for the
            `datapackage.json` file. If the :data:`descriptor` parameter was the
            path to the `datapackage.json`, this will automatically be set to
            its base path.

    Raises:
        DataPackageException: If the :data:`descriptor` couldn't be loaded or was
            invalid.
        SchemaError: If the :data:`schema` couldn't be loaded or was invalid.
        RegistryError: If there was some problem loading the :data:`schema`
            from the registry.
    """

    # Public

    def __init__(self, descriptor=None, schema=None, default_base_path=None):

        # Extract from zip
        descriptor = self._extract_zip_if_possible(descriptor)

        # Get base path
        self._base_path = helpers.get_descriptor_base_path(descriptor) or default_base_path

        # Process actions
        self._descriptor = helpers.retrieve_descriptor(descriptor)
        helpers.dereference_data_package_descriptor(self._descriptor, self._base_path)
        helpers.expand_data_package_descriptor(self._descriptor)

        # Get profile
        profile = self._descriptor['profile']

        # Handle deprecated schema argument
        if schema is not None:
            warnings.warn(
                'Argument "schema" is deprecated. '
                'Please use "descriptor.profile" property.',
                UserWarning)
            if isinstance(schema, six.string_types):
                if schema in ['base', 'default']:
                    schema = 'data-package'
                elif schema == 'tabular':
                    schema = 'tabular-data-package'
                elif schema == 'fiscal':
                    schema = 'fiscal-data-package'
            profile = schema

        # Handle deprecated resource.path/url
        for resource in self._descriptor.get('resources', []):
            url = resource.pop('url', None)
            if url is not None:
                warnings.warn(
                    'Resource property "url: <url>" is deprecated. '
                    'Please use "path: [url]" instead (as array).',
                    UserWarning)
                resource['path'] = [url]
            path = resource.get('path', None)
            if isinstance(path, six.string_types):
                warnings.warn(
                    'Resource property "path: <path>" is deprecated. '
                    'Please use "path: [path]" instead (as array).',
                    UserWarning)
                resource['path'] = [path]

        # Set attributes
        self._profile = Profile(profile)
        self._resources = self._update_resources((), self.descriptor, self.base_path)

    def __del__(self):
        if hasattr(self, '_tempdir') and os.path.exists(self._tempdir):
            shutil.rmtree(self._tempdir, ignore_errors=True)

    @property
    def descriptor(self):
        """"dict: The descriptor of this data package. Its attributes can be
        changed.
        """
        return self._descriptor

    @property
    def profile(self):
        """"str: The profile of this data package.
        """
        return self._profile

    @property
    def resources(self):
        """"The resources defined in this data package (can be empty).

        To add or remove resources, alter the `resources` attribute of the
        :data:`descriptor`.

        :returns: The resources.
        :rtype: tuple of :class:`.Resource`

        """
        self._resources = self._update_resources(self._resources,
                                                 self.descriptor,
                                                 self.base_path)
        return self._resources

    def save(self, file_or_path):
        """"Validates and saves this Data Package contents into a zip file.

        It creates a zip file into ``file_or_path`` with the contents of this
        Data Package and its resources. Every resource which content lives in
        the local filesystem will be copied to the zip file. Consider the
        following Data Package descriptor::

            {
                "name": "gdp",
                "resources": [
                    {"name": "local", "format": "CSV", "path": "data.csv"},
                    {"name": "inline", "data": [4, 8, 15, 16, 23, 42]},
                    {"name": "remote", "url": "http://someplace.com/data.csv"}
                ]
            }

        The final structure of the zip file will be::

            ./datapackage.json
            ./data/local.csv

        With the contents of `datapackage.json` being the same as returned by
        :func:`to_json`.

        The resources' file names are generated based on their `name` and
        `format` fields if they exist. If the resource has no `name`, it'll be
        used `resource-X`, where `X` is the index of the resource in the
        `resources` list (starting at zero). If the resource has `format`,
        it'll be lowercased and appended to the `name`, becoming
        "`name.format`".

        Args:
            file_or_path (string or file-like object): The file path or a
                file-like object where the contents of this Data Package will
                be saved into.

        Raises:
            ValidationError: If the Data Package is invalid.
            DataPackageException: If there was some error writing the package.

        """
        self.validate()

        def arcname(resource):
            basename = resource.descriptor.get('name')
            resource_format = resource.descriptor.get('format')
            if not basename:
                index = self.resources.index(resource)
                basename = 'resource-{index}'.format(index=index)
            if resource_format:
                basename = '.'.join([basename, resource_format.lower()])
            return os.path.join('data', basename)

        try:
            with zipfile.ZipFile(file_or_path, 'w') as z:
                descriptor = json.loads(self.to_json())
                for i, resource in enumerate(self.resources):
                    path = None
                    if resource.source_type == 'local':
                        path = os.path.abspath(resource.source)
                    if path:
                        path_inside_dp = arcname(resource)
                        z.write(path, path_inside_dp)
                        descriptor['resources'][i]['path'] = path_inside_dp
                z.writestr('datapackage.json', json.dumps(descriptor))
        except (IOError,
                zipfile.BadZipfile,
                zipfile.LargeZipFile) as e:
            six.raise_from(exceptions.DataPackageException(e), e)

    def validate(self):
        """"Validate this Data Package.

        Raises:
            ValidationError: If the Data Package is invalid.

        """
        descriptor = self.to_dict()
        self.profile.validate(descriptor)

    def iter_errors(self):
        """"Lazily yields each ValidationError for the received data dict.

        Returns:
            iter: ValidationError for each error in the data.

        """
        return self.profile.iter_errors(self.to_dict())

    # Additional

    @property
    def base_path(self):
        """"str: The base path of this Data Package (can be None).
        """
        return self._base_path

    def to_dict(self):
        """"dict: Convert this Data Package to dict.
        """
        return copy.deepcopy(self.descriptor)

    def to_json(self):
        """"str: Convert this Data Package to a JSON string.
        """
        return json.dumps(self.descriptor)

    # Private

    def _extract_zip_if_possible(self, descriptor):
        """"str: Path to the extracted datapackage.json if descriptor points to
        ZIP, or the unaltered descriptor otherwise.
        """
        result = descriptor
        try:
            if isinstance(descriptor, six.string_types):
                res = requests.get(descriptor)
                res.raise_for_status()
                result = res.content
        except (IOError,
                ValueError,
                requests.exceptions.RequestException):
            pass

        try:
            the_zip = result
            if isinstance(the_zip, bytes):
                try:
                    os.path.isfile(the_zip)
                except (TypeError, ValueError):
                    # the_zip contains the zip file contents
                    the_zip = io.BytesIO(the_zip)

            if zipfile.is_zipfile(the_zip):
                with zipfile.ZipFile(the_zip, 'r') as z:
                    self._validate_zip(z)

                    descriptor_path = [f for f in z.namelist()
                                       if f.endswith('datapackage.json')][0]

                    self._tempdir = tempfile.mkdtemp('-datapackage')
                    z.extractall(self._tempdir)
                    result = os.path.join(self._tempdir, descriptor_path)
            else:
                result = descriptor
        except (TypeError,
                zipfile.BadZipfile):
            pass

        if hasattr(descriptor, 'seek'):
            # Rewind descriptor if it's a file, as we read it for testing if it's
            # a zip file
            descriptor.seek(0)

        return result

    def _validate_zip(self, the_zip):
        datapackage_jsons = [f for f in the_zip.namelist()
                             if f.endswith('datapackage.json')]
        if len(datapackage_jsons) != 1:
            msg = 'DataPackage must have only one "datapackage.json" (had {n})'
            raise exceptions.DataPackageException(msg.format(n=len(datapackage_jsons)))

    def _update_resources(self, current_resources, descriptor, base_path):
        resources_dicts = descriptor.get('resources')
        new_resources = []

        if resources_dicts is not None:
            for resource_dict in resources_dicts:
                resource = [res for res in current_resources
                            if res.descriptor == resource_dict]
                if not resource:
                    resource = [Resource(resource_dict, base_path)]
                new_resources.append(resource[0])

        return tuple(new_resources)

    # Deprecated

    def safe(self):
        """True: datapackage is always safe.
        """

        # Deprecate
        warnings.warn(
            'DataPackage.safe is deprecated. '
            'Now it\'s always safe.',
            UserWarning)

        return True

    @property
    def schema(self):
        """:class:`.Schema`: This data package's schema.
        """

        # Deprecate
        warnings.warn(
            'DataPackage.schema is deprecated.',
            UserWarning)
        required = ()

        return self._profile

    @property
    def attributes(self):
        """tuple: Attributes defined in the schema and the data package.
        """

        # Deprecate
        warnings.warn(
            'DataPackage.attributes is deprecated.',
            UserWarning)

        # Get attributes
        attributes = set(self.to_dict().keys())
        try:
            attributes.update(self.profile.properties.keys())
        except AttributeError:
            pass

        return tuple(attributes)

    @property
    def required_attributes(self):
        """tuple: The schema's required attributed.
        """

        # Deprecate
        warnings.warn(
            'DataPackage.attributes_attributes is deprecated.',
            UserWarning)
        required = ()

        # Get required
        try:
            if self.profile.required is not None:
                required = tuple(self.profile.required)
        except AttributeError:
            pass

        return required

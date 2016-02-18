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
import datapackage.schema
from .resource import Resource
from .exceptions import (
    DataPackageException,
)


class DataPackage(object):
    '''Class for loading, validating and working with a Data Package.

    Args:
        metadata (dict, str or file-like object, optional): The contents of the
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
            `datapackage.json` file. If the :data:`metadata` parameter was the
            path to the `datapackage.json`, this will automatically be set to
            its base path.

    Raises:
        DataPackageException: If the :data:`metadata` couldn't be loaded or was
            invalid.
        SchemaError: If the :data:`schema` couldn't be loaded or was invalid.
        RegistryError: If there was some problem loading the :data:`schema`
            from the registry.
    '''

    def __init__(self, metadata=None, schema='base', default_base_path=None):
        metadata = self._extract_zip_if_possible(metadata)

        self._metadata = self._load_metadata(metadata)
        self._schema = self._load_schema(schema)
        self._base_path = self._get_base_path(metadata, default_base_path)
        self._resources = self._load_resources(self.metadata,
                                               self.base_path)

    def __del__(self):
        self._remove_tempdir_if_exists()

    @property
    def metadata(self):
        '''dict: The metadata of this data package. Its attributes can be
        changed.'''
        return self._metadata

    @property
    def schema(self):
        ''':class:`.Schema`: This data package's schema.

        Check https://github.com/okfn/datapackage-validate-py for documentation
        on its attributes.
        '''
        return self._schema

    @property
    def base_path(self):
        '''str: The base path of this Data Package (can be None).'''
        return self._base_path

    @property
    def resources(self):
        '''The resources defined in this data package (can be empty).

        To add or remove resources, alter the `resources` attribute of the
        :data:`metadata`.

        :returns: The resources.
        :rtype: tuple of :class:`.Resource`
        '''
        self._resources = self._update_resources(self._resources,
                                                 self.metadata,
                                                 self.base_path)
        return self._resources

    @property
    def attributes(self):
        '''tuple: The union of the attributes defined in the schema and the
        data package (can be empty).'''
        attributes = set(self.to_dict().keys())
        try:
            attributes.update(self.schema.properties.keys())
        except AttributeError:
            pass
        return tuple(attributes)

    @property
    def required_attributes(self):
        '''tuple: The schema's required attributed (can be empty).'''
        required = ()
        try:
            if self.schema.required is not None:
                required = tuple(self.schema.required)
        except AttributeError:
            pass
        return required

    def to_dict(self):
        '''dict: Convert this Data Package to dict.'''
        return copy.deepcopy(self.metadata)

    def to_json(self):
        '''str: Convert this Data Package to a JSON string.'''
        return json.dumps(self.metadata)

    def safe(self):
        '''bool: Return if it's safe to load this datapackage's resources.

        A Data Package is safe if it has no resources, or if all of its
        resources are either:
            * Inline;
            * Remote;
            * Local relative to the Data Package's base path.

        Even though we don't check the remote resources' URLs, keep in mind
        that they can be an attack vector as well. For example, a malicious
        user may set a resource URL to an address only accessible by the
        machine that's parsing the datapackage. That might be a problem or not,
        depending on your specific usage.
        '''
        local_resources = [resource for resource in self.resources
                           if resource.local_data_path]
        if not self.base_path:
            return len(local_resources) == 0
        else:
            for resource in local_resources:
                if not resource.local_data_path.startswith(self.base_path):
                    return False

        return True

    def save(self, file_or_path):
        '''Validates and saves this Data Package contents into a zip file.

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
        '''
        self.validate()

        def arcname(resource):
            basename = resource.metadata.get('name')
            resource_format = resource.metadata.get('format')
            if not basename:
                index = self.resources.index(resource)
                basename = 'resource-{index}'.format(index=index)
            if resource_format:
                basename = '.'.join([basename, resource_format.lower()])
            return os.path.join('data', basename)

        try:
            with zipfile.ZipFile(file_or_path, 'w') as z:
                metadata = json.loads(self.to_json())
                for i, resource in enumerate(self.resources):
                    path = resource.local_data_path
                    if path:
                        path_inside_dp = arcname(resource)
                        z.write(path, path_inside_dp)
                        metadata['resources'][i]['path'] = path_inside_dp
                z.writestr('datapackage.json', json.dumps(metadata))
        except (IOError,
                zipfile.BadZipfile,
                zipfile.LargeZipFile) as e:
            six.raise_from(DataPackageException(e), e)

    def validate(self):
        '''Validate this Data Package.

        Raises:
            ValidationError: If the Data Package is invalid.
        '''
        self.schema.validate(self.to_dict())

    def iter_errors(self):
        '''Lazily yields each ValidationError for the received data dict.

        Returns:
            iter: ValidationError for each error in the data.
        '''
        return self.schema.iter_errors(self.to_dict())

    def _extract_zip_if_possible(self, metadata):
        '''str: Path to the extracted datapackage.json if metadata points to
        ZIP, or the unaltered metadata otherwise.'''
        result = metadata
        try:
            if isinstance(metadata, six.string_types):
                res = requests.get(metadata)
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
                result = metadata
        except (TypeError,
                zipfile.BadZipfile):
            pass

        if hasattr(metadata, 'seek'):
            # Rewind metadata if it's a file, as we read it for testing if it's
            # a zip file
            metadata.seek(0)

        return result

    def _validate_zip(self, the_zip):
        datapackage_jsons = [f for f in the_zip.namelist()
                             if f.endswith('datapackage.json')]
        if len(datapackage_jsons) != 1:
            msg = 'DataPackage must have only one "datapackage.json" (had {n})'
            raise DataPackageException(msg.format(n=len(datapackage_jsons)))

    def _load_metadata(self, metadata):
        the_metadata = metadata

        if the_metadata is None:
            the_metadata = {}

        if isinstance(the_metadata, six.string_types):
            try:
                if os.path.isfile(the_metadata):
                    with open(the_metadata, 'r') as f:
                        the_metadata = json.load(f)
                else:
                    req = requests.get(the_metadata)
                    req.raise_for_status()
                    the_metadata = req.json()
            except (IOError,
                    ValueError,
                    requests.exceptions.RequestException) as e:
                msg = 'Unable to load JSON at \'{0}\''.format(metadata)
                six.raise_from(DataPackageException(msg), e)

        if hasattr(the_metadata, 'read'):
            try:
                the_metadata = json.load(the_metadata)
            except ValueError as e:
                six.raise_from(DataPackageException(str(e)), e)

        if not isinstance(the_metadata, dict):
            msg = 'Data must be a \'dict\', but was a \'{0}\''
            raise DataPackageException(msg.format(type(the_metadata).__name__))

        return the_metadata

    def _load_schema(self, schema):
        return datapackage.schema.Schema(schema)

    def _get_base_path(self, metadata, default_base_path):
        base_path = default_base_path

        if isinstance(metadata, six.string_types):
            if os.path.exists(metadata):
                base_path = os.path.dirname(os.path.abspath(metadata))
            else:
                # suppose metadata is a URL
                base_path = os.path.dirname(metadata)

        return base_path

    def _load_resources(self, metadata, base_path):
        return self._update_resources((), metadata, base_path)

    def _update_resources(self, current_resources, metadata, base_path):
        resources_dicts = metadata.get('resources')
        new_resources = []

        if resources_dicts is not None:
            for resource_dict in resources_dicts:
                resource = [res for res in current_resources
                            if res.metadata == resource_dict]
                if not resource:
                    resource = [Resource.load(resource_dict, base_path)]
                new_resources.append(resource[0])

        return tuple(new_resources)

    def _remove_tempdir_if_exists(self):
        if hasattr(self, '_tempdir') and os.path.exists(self._tempdir):
            shutil.rmtree(self._tempdir, ignore_errors=True)

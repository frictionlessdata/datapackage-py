from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import re
import six
import json
import copy
import glob
import shutil
import zipfile
import requests
import warnings
import tempfile
from copy import deepcopy
from tableschema import Storage
from .resource import Resource
from .profile import Profile
from . import exceptions
from . import helpers
from . import config


# Module API

class Package(object):

    # Public

    def __init__(self, descriptor=None, base_path=None, strict=False, storage=None,
                 # Deprecated
                 schema=None, default_base_path=None, **options):
        """https://github.com/frictionlessdata/datapackage-py#package
        """

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
                descriptor['profile'] = schema

        # Handle deprecated default_base_path argument
        if default_base_path is not None:
            warnings.warn(
                'Argument "default_base_path" is deprecated. '
                'Please use "base_path" argument.',
                UserWarning)
            base_path = default_base_path

        # Extract from zip
        tempdir, descriptor = _extract_zip_if_possible(descriptor)
        if tempdir:
            self.__tempdir = tempdir

        # Get base path
        if base_path is None:
            base_path = helpers.get_descriptor_base_path(descriptor)

        # Instantiate storage
        if storage and not isinstance(storage, Storage):
            storage = Storage.connect(storage, **options)

        # Get descriptor from storage
        if storage and not descriptor:
            descriptor = {'resources': []}
            for bucket in storage.buckets:
                descriptor['resources'].append({'path': bucket})

        # Process descriptor
        descriptor = helpers.retrieve_descriptor(descriptor)
        descriptor = helpers.dereference_package_descriptor(descriptor, base_path)

        # Handle deprecated resource.path/url
        for resource in descriptor.get('resources', []):
            url = resource.pop('url', None)
            if url is not None:
                warnings.warn(
                    'Resource property "url: <url>" is deprecated. '
                    'Please use "path: [url]" instead (as array).',
                    UserWarning)
                resource['path'] = [url]

        # Set attributes
        self.__current_descriptor = deepcopy(descriptor)
        self.__next_descriptor = deepcopy(descriptor)
        self.__base_path = base_path
        self.__storage = storage
        self.__strict = strict
        self.__resources = []
        self.__errors = []

        # Build package
        self.__build()

    def __del__(self):
        """https://github.com/frictionlessdata/tableschema-py#schema
        """
        if hasattr(self, '_tempdir') and os.path.exists(self.__tempdir):
            shutil.rmtree(self.__tempdir, ignore_errors=True)

    @property
    def valid(self):
        """https://github.com/frictionlessdata/tableschema-py#schema
        """
        return not bool(self.__errors)

    @property
    def errors(self):
        """https://github.com/frictionlessdata/tableschema-py#schema
        """
        return self.__errors

    @property
    def profile(self):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        return self.__profile

    @property
    def descriptor(self):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        # Never use self.descriptor inside this class (!!!)
        return self.__next_descriptor

    @property
    def resources(self):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        return self.__resources

    @property
    def resource_names(self):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        return [resource.name for resource in self.resources]

    def get_resource(self, name):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        for resource in self.resources:
            if resource.name == name:
                return resource
        return None

    def add_resource(self, descriptor):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        self.__current_descriptor.setdefault('resources', [])
        self.__current_descriptor['resources'].append(descriptor)
        self.__build()
        return self.__resources[-1]

    def remove_resource(self, name):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        resource = self.get_resource(name)
        if resource:
            predicat = lambda resource: resource.get('name') != name
            self.__current_descriptor['resources'] = list(filter(
                predicat, self.__current_descriptor['resources']))
            self.__build()
        return resource

    def infer(self, pattern=False):
        """https://github.com/frictionlessdata/datapackage-py#package
        """

        # Files
        if pattern:

            # No base path
            if not self.__base_path:
                message = 'Base path is required for pattern infer'
                raise exceptions.DataPackageException(message)

            # Add resources
            options = {'recursive': True} if '**' in pattern else {}
            for path in glob.glob(os.path.join(self.__base_path, pattern), **options):
                self.add_resource({'path': os.path.relpath(path, self.__base_path)})

        # Resources
        for index, resource in enumerate(self.resources):
            descriptor = resource.infer()
            self.__current_descriptor['resources'][index] = descriptor
            self.__build()

        # Profile
        if self.__next_descriptor['profile'] == config.DEFAULT_DATA_PACKAGE_PROFILE:
            if self.resources and all(map(lambda resource: resource.tabular, self.resources)):
                self.__current_descriptor['profile'] = 'tabular-data-package'
                self.__build()

        return self.__current_descriptor

    def commit(self, strict=None):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        if strict is not None:
            self.__strict = strict
        elif self.__current_descriptor == self.__next_descriptor:
            return False
        self.__current_descriptor = deepcopy(self.__next_descriptor)
        self.__build()
        return True

    def save(self, target=None, storage=None, **options):
        """https://github.com/frictionlessdata/datapackage-py#package
        """

        # Save package to storage
        if storage is not None:
            if not isinstance(storage, Storage):
                storage = Storage.connect(storage, **options)
            buckets = []
            schemas = []
            for resource in self.resources:
                if resource.tabular:
                    resource.infer()
                    buckets.append(_slugify_resource_name(resource.name))
                    schemas.append(resource.schema.descriptor)
            schemas = list(map(_slugify_foreign_key, schemas))
            storage.create(buckets, schemas, force=True)
            for bucket in storage.buckets:
                resource = self.resources[buckets.index(bucket)]
                storage.write(bucket, resource.iter())

        # Save descriptor to json
        elif str(target).endswith('.json'):
            mode = 'w'
            encoding = 'utf-8'
            if six.PY2:
                mode = 'wb'
                encoding = None
            helpers.ensure_dir(target)
            with io.open(target, mode=mode, encoding=encoding) as file:
                json.dump(self.__current_descriptor, file, indent=4)

        # Save package to zip
        else:
            try:
                with zipfile.ZipFile(target, 'w') as z:
                    descriptor = json.loads(json.dumps(self.__current_descriptor))
                    for index, resource in enumerate(self.resources):
                        if not resource.name:
                            continue
                        if not resource.local:
                            continue
                        path = os.path.abspath(resource.source)
                        basename = resource.descriptor.get('name')
                        resource_format = resource.descriptor.get('format')
                        if resource_format:
                            basename = '.'.join([basename, resource_format.lower()])
                        path_inside_dp = os.path.join('data', basename)
                        z.write(path, path_inside_dp)
                        descriptor['resources'][index]['path'] = path_inside_dp
                    z.writestr('datapackage.json', json.dumps(descriptor))
            except (IOError, zipfile.BadZipfile, zipfile.LargeZipFile) as exception:
                six.raise_from(exceptions.DataPackageException(exception), exception)

        return True

    # Private

    def __build(self):

        # Process descriptor
        expand = helpers.expand_package_descriptor
        self.__current_descriptor = expand(self.__current_descriptor)
        self.__next_descriptor = deepcopy(self.__current_descriptor)

        # Instantiate profile
        self.__profile = Profile(self.__current_descriptor.get('profile'))

        # Validate descriptor
        try:
            self.__profile.validate(self.__current_descriptor)
            self.__errors = []
        except exceptions.ValidationError as exception:
            self.__errors = exception.errors
            if self.__strict:
                raise exception

        # Update resource
        descriptors = self.__current_descriptor.get('resources', [])
        self.__resources = self.__resources[:len(descriptors)]
        iterator = enumerate(six.moves.zip_longest(list(self.__resources), descriptors))
        for index, (resource, descriptor) in iterator:
            if (not resource or resource.descriptor != descriptor or
                    (resource.schema and resource.schema.foreign_keys)):
                updated_resource = Resource(descriptor,
                    strict=self.__strict,
                    base_path=self.__base_path,
                    storage=self.__storage,
                    package=self)
                if not resource:
                    self.__resources.append(updated_resource)
                else:
                    self.__resources[index] = updated_resource

    # Deprecated

    def safe(self):
        """True: datapackage is always safe.
        """

        # Deprecate
        warnings.warn(
            'Property "package.safe" is deprecated. '
            'Now it\'s always safe.',
            UserWarning)

        return True

    @property
    def schema(self):
        """:class:`.Schema`: This data package's schema.
        """

        # Deprecate
        warnings.warn(
            'Property "package.schema" is deprecated.',
            UserWarning)

        return self.__profile

    @property
    def attributes(self):
        """tuple: Attributes defined in the schema and the data package.
        """

        # Deprecate
        warnings.warn(
            'Property "package.attributes" is deprecated.',
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
            'Property "package.required_attributes" is deprecated.',
            UserWarning)
        required = ()

        # Get required
        try:
            if self.profile.required is not None:
                required = tuple(self.profile.required)
        except AttributeError:
            pass

        return required

    def validate(self):
        """"Validate this Data Package.
        """

        # Deprecate
        warnings.warn(
            'Property "package.validate" is deprecated.',
            UserWarning)

        descriptor = self.to_dict()
        self.profile.validate(descriptor)

    def iter_errors(self):
        """"Lazily yields each ValidationError for the received data dict.
        """

        # Deprecate
        warnings.warn(
            'Property "package.iter_errors" is deprecated.',
            UserWarning)

        return self.profile.iter_errors(self.to_dict())

    @property
    def base_path(self):
        """"str: The base path of this Data Package (can be None).
        """

        # Deprecate
        warnings.warn(
            'Property "package.base_path" is deprecated.',
            UserWarning)

        return self.__base_path

    def to_dict(self):
        """"dict: Convert this Data Package to dict.
        """

        # Deprecate
        warnings.warn(
            'Property "package.to_dict" is deprecated.',
            UserWarning)

        return copy.deepcopy(self.descriptor)

    def to_json(self):
        """"str: Convert this Data Package to a JSON string.
        """

        # Deprecate
        warnings.warn(
            'Property "package.to_json" is deprecated.',
            UserWarning)

        return json.dumps(self.descriptor)


# Internal

def _extract_zip_if_possible(descriptor):
    """If descriptor is a path to zip file extract and return (tempdir, descriptor)
    """
    tempdir = None
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
                _validate_zip(z)
                descriptor_path = [
                    f for f in z.namelist() if f.endswith('datapackage.json')][0]
                tempdir = tempfile.mkdtemp('-datapackage')
                z.extractall(tempdir)
                result = os.path.join(tempdir, descriptor_path)
        else:
            result = descriptor
    except (TypeError,
            zipfile.BadZipfile):
        pass
    if hasattr(descriptor, 'seek'):
        # Rewind descriptor if it's a file, as we read it for testing if it's
        # a zip file
        descriptor.seek(0)
    return (tempdir, result)


def _validate_zip(the_zip):
    """Validate zipped data package
    """
    datapackage_jsons = [f for f in the_zip.namelist() if f.endswith('datapackage.json')]
    if len(datapackage_jsons) != 1:
        msg = 'DataPackage must have only one "datapackage.json" (had {n})'
        raise exceptions.DataPackageException(msg.format(n=len(datapackage_jsons)))


def _slugify_resource_name(name):
    """Slugify resource name
    """
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)


def _slugify_foreign_key(schema):
    """Slugify foreign key
    """
    for foreign_key in schema.get('foreignKeys', []):
        foreign_key['reference']['resource'] = _slugify_resource_name(
            foreign_key['reference'].get('resource', ''))
    return schema

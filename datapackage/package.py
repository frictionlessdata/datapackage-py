from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
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
from .resource import Resource
from .profile import Profile
from . import exceptions
from . import helpers
from . import config


# Module API

class Package(object):

    # Public

    def __init__(self, descriptor=None, base_path=None, strict=False,
                 # Deprecated
                 schema=None, default_base_path=None):
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
        descriptor = self.__extract_zip_if_possible(descriptor)

        # Get base path
        if base_path is None:
            base_path = helpers.get_descriptor_base_path(descriptor)

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
        self.__strict = strict
        self.__resources = []
        self.__errors = []

        # Build package
        self.__build()

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
        self.__next_descriptor.setdefault('resources', [])
        self.__next_descriptor['resources'].append(descriptor)
        self.commit()
        return self.__resources[-1]

    def remove_resource(self, name):
        """https://github.com/frictionlessdata/datapackage-py#package
        """
        resource = self.get_resource(name)
        if resource:
            predicat = lambda resource: resource.get('name') != name
            self.__next_descriptor['resources'] = filter(
                predicat, self.__next_descriptor['resources'])
            self.commit()
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
            self.__next_descriptor['resources'][index] = descriptor
            self.commit()

        # Profile
        if self.__next_descriptor['profile'] == config.DEFAULT_DATA_PACKAGE_PROFILE:
            if self.resources and all(map(lambda resource: resource.tabular, self.resources)):
                self.__next_descriptor['profile'] = 'tabular-data-package'
                self.commit()

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

    def save(self, target):
        """https://github.com/frictionlessdata/datapackage-py#package
        """

        # Produce resource name
        def arcname(resource):
            basename = resource.descriptor.get('name')
            resource_format = resource.descriptor.get('format')
            if not basename:
                index = self.resources.index(resource)
                basename = 'resource-{index}'.format(index=index)
            if resource_format:
                basename = '.'.join([basename, resource_format.lower()])
            return os.path.join('data', basename)

        # Save data package
        try:
            with zipfile.ZipFile(target, 'w') as z:
                descriptor = json.loads(self.to_json())
                for i, resource in enumerate(self.resources):
                    path = None
                    if resource.local:
                        path = os.path.abspath(resource.source)
                    if path:
                        path_inside_dp = arcname(resource)
                        z.write(path, path_inside_dp)
                        descriptor['resources'][i]['path'] = path_inside_dp
                z.writestr('datapackage.json', json.dumps(descriptor))

        # Saving error
        except (IOError,
                zipfile.BadZipfile,
                zipfile.LargeZipFile) as e:
            six.raise_from(exceptions.DataPackageException(e), e)

        return True

    # Private

    def __build(self):

        # Process descriptor
        self.__current_descriptor = helpers.expand_package_descriptor(
            self.__current_descriptor)
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
            if not resource or resource.descriptor != descriptor:
                updated_resource = Resource(
                    descriptor, strict=self.__strict, base_path=self.__base_path)
                if not resource:
                    self.__resources.append(updated_resource)
                else:
                    self.__resources[index] = updated_resource

    def __extract_zip_if_possible(self, descriptor):
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
                    self.__validate_zip(z)
                    descriptor_path = [
                        f for f in z.namelist() if f.endswith('datapackage.json')][0]
                    self.__tempdir = tempfile.mkdtemp('-datapackage')
                    z.extractall(self.__tempdir)
                    result = os.path.join(self.__tempdir, descriptor_path)
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

    def __validate_zip(self, the_zip):
        datapackage_jsons = [f for f in the_zip.namelist() if f.endswith('datapackage.json')]
        if len(datapackage_jsons) != 1:
            msg = 'DataPackage must have only one "datapackage.json" (had {n})'
            raise exceptions.DataPackageException(msg.format(n=len(datapackage_jsons)))

    def __update_resources(self, current_resources, descriptor, base_path):
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

    def __del__(self):
        if hasattr(self, '_tempdir') and os.path.exists(self.__tempdir):
            shutil.rmtree(self.__tempdir, ignore_errors=True)

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

        return self.__profile

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

    @property
    def base_path(self):
        """"str: The base path of this Data Package (can be None).
        """
        return self.__base_path

    def to_dict(self):
        """"dict: Convert this Data Package to dict.
        """
        return copy.deepcopy(self.descriptor)

    def to_json(self):
        """"str: Convert this Data Package to a JSON string.
        """
        return json.dumps(self.descriptor)

import os
import sys
import urllib
import hashlib

if sys.version_info[0] < 3:
    import urlparse
    urllib.parse = urlparse
    urllib.request = urllib
    next = lambda x: x.next()
    bytes = str
    str = unicode

from . import sources
from . import licenses


class Resource(object):

    def __init__(self, descriptor):
        self.descriptor = descriptor

    @property
    def data(self):
        """A field containing the data directly inline in the datapackage.json
        file.

        """
        return self.descriptor.get('data', None)

    @property
    def path(self):
        """Unix-style ('/') relative path to the resource. Path MUST be a
        relative path, that is relative to the directory in which the
        descriptor file (datapackage.json) listing this file resides,
        or relative to the URI specified by the optional base property
        (if it is defined).

        """
        return self.descriptor.get('path', None)

    @property
    def url(self):
        """The url of this data resource"""
        return self.descriptor.get('url', None)

    @property
    def name(self):
        """A resource SHOULD contain an name attribute. The name is a simple
        name or identifier to be used for this resource.

        The name SHOULD be usable in a url path and SHOULD therefore
        consist only of alphanumeric characters plus ".", "-" and "_".

        It would be usual for the name to correspond to the file name
        (minus the extension) of the data file the resource describes.

        """
        return self.descriptor.get('name', u'')

    @property
    def format(self):
        """A format like 'csv', 'xls', 'json', etc. Would be expected to be
        the the standard file extension for this type of resource.

        """
        fmt = self.descriptor.get('format', None)
        if not fmt and self.path:
            fmt = os.path.splitext(self.path)[1]
        return fmt

    @property
    def mediatype(self):
        """The mediatype/mimetype of the resource, e.g. 'text/csv',
        'application/vnd.ms-excel'.

        """
        return self.descriptor.get('mediatype', None)

    @property
    def encoding(self):
        """Specify the character encoding of a resource data file. The values
        should be one of the "Preferred MIME Names" for a character
        encoding registered with IANA. If no value for this key is
        specified then the default is UTF-8.

        """
        return self.descriptor.get('encoding', u'utf-8')

    @property
    def bytes(self):
        """The size of the file in bytes."""
        return self.descriptor.get('bytes', None)

    def _data_bytes(self):
        # need to make sure the data is in the proper encoding, I
        # think? It should just be a JSON object or string, but does
        # that mean that len() is sufficient or not?
        raise NotImplementedError

    def _path_bytes(self):
        if not self.path:
            raise ValueError("path to file is not specified")
        size = os.path.getsize(self.path)
        return size

    def _url_bytes(self):
        if not self.url:
            raise ValueError("url to file is not specified")
        site = urllib.urlopen(self.url)
        meta = site.info()
        size = meta.getheaders("Content-Length")[0]
        return size

    def update_bytes(self):
        old_size = self.bytes
        if self.data:
            new_size = self._data_bytes()
        elif self.path:
            new_size = self._path_bytes()
        elif self.url:
            new_size = self._url_bytes()
        else:
            raise ValueError("resource not found")

        if old_size and (old_size != new_size):
            raise RuntimeError(
                "size of file has changed! (was: {}, is now: {})".format(
                    old_size, new_size))

        self.descriptor['bytes'] = new_size

    @property
    def hash(self):
        """The MD5 hash for this resource."""
        return self.descriptor.get('hash', None)

    def _data_hash(self):
        md5 = hashlib.md5()
        md5.update(self.data)
        hash = md5.hexdigest()
        return hash

    def _path_hash(self):
        """Computes the md5 checksum of the file saved at the given path."""
        # we need to compute the md5 sum one chunk at a time, because
        # some files are too large to fit in memory
        if not self.path:
            raise ValueError("path to file is not specified")
        md5 = hashlib.md5()
        with open(self.path, 'rb') as fh:
            while True:
                chunk = fh.read(128)
                if not chunk:
                    break
                md5.update(chunk)
        hash = md5.hexdigest()
        return hash

    def _url_hash(self):
        # probably want to download the data first and store it
        # somewhere before computing the MD5 sum otherwise it'll have
        # be downloaded twice. But then if that's the case then
        # _path_hash can probably just be used?
        raise NotImplementedError

    def update_hash(self):
        old_hash = self.hash
        if self.data:
            new_hash = self._data_hash()
        elif self.path:
            new_hash = self._path_hash()
        elif self.url:
            new_hash = self._url_hash()
        else:
            raise ValueError("resource not found")

        if old_hash and (old_hash != new_hash):
            raise RuntimeError(
                "hash of file has changed! (was: {}, is now: {})".format(
                    old_hash, new_hash))

        self.descriptor['hash'] = new_hash

    @property
    def schema(self):
        """A schema for the resource, e.g. in the case of tabular data.

        """
        return self.descriptor.get('schema', u'')

    @property
    def sources(self):
        """An array of source hashes. Each source hash may have name, web and
        email fields.

        Defaults to an empty list.

        """
        return sources.get_sources(self.descriptor)

    @sources.setter
    def sources(self, val):
        sources.set_sources(self.descriptor, val)

    def add_source(self, name, web=None, email=None):
        """Adds a source to the list of sources for this datapackage.

        :param string name: The human-readable name of the source.
        :param string web: A URL pointing to the source.
        :param string email: An email address for the contact of the
            source.

        """
        sources.add_source(self.descriptor, name, web, email)

    def remove_source(self, name):
        """Removes the source with the given name."""
        sources.remove_source(self.descriptor, name)

    @property
    def licenses(self):
        """MUST be an array. Each entry MUST be a hash with a type and a url
        property linking to the actual text. The type SHOULD be an
        Open Definition license ID if an ID exists for the license and
        otherwise may be the general license name or identifier.

        """
        licenses.get_licenses(self.descriptor)

    @licenses.setter
    def licenses(self, val):
        licenses.set_licenses(self.descriptor, val)

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
        licenses.add_license(self.descriptor, license_type, url)

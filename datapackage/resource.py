import os
import sys
import urllib
import hashlib
import json
import posixpath
import re
import mimetypes

if sys.version_info[0] < 3:
    import urlparse
    urllib.parse = urlparse
    urllib.request = urllib
    next = lambda x: x.next()
    bytes = str
    str = unicode

from . import sources
from . import licenses
from .util import is_local, is_url, is_mimetype

name_regex = re.compile(r"^[0-9A-Za-z-_\.]+$")


class Resource(object):

    def __init__(self, datapackage_uri, descriptor, opener=None):
        self.datapackage_uri = datapackage_uri
        self.descriptor = descriptor
        self.is_local = is_local(self.datapackage_uri)

    def _open(self, mode):
        if self.is_local:
            return open(self.fullpath, mode)
        else:
            if mode not in ('r', 'rb'):
                raise ValueError('urls can only be opened read-only')
            return urllib.urlopen(self.fullpath)

    @property
    def data(self):
        """A field containing the data directly inline in the datapackage.json
        file.

        """
        return self.descriptor.get('data', None)

    @data.setter
    def data(self, val):
        if not val and 'data' in self.descriptor:
            del self.descriptor['data']
            return

        # make sure the value is json serializable
        try:
            val = json.loads(json.dumps(val))
        except TypeError:
            raise TypeError("'{}' is not json serializable".format(val))

        self.descriptor['data'] = val

    @property
    def path(self):
        """Unix-style ('/') relative path to the resource. Path MUST be a
        relative path, that is relative to the directory in which the
        descriptor file (datapackage.json) listing this file resides,
        or relative to the URI specified by the optional base property
        (if it is defined).

        """
        return self.descriptor.get('path', None)

    @path.setter
    def path(self, val):
        if not val and 'path' in self.descriptor:
            del self.descriptor['path']
            return

        # use posix path since it is supposed to be unix-style
        self.descriptor['path'] = str(val)

        self.mediatype = self._guess_mediatype()
        self.format = self._guess_format()

    @property
    def fullpath(self):
        """The full path to the resource. Like 'path', this is a Unix-style
        path, but includes the datapackage uri in the path, rather
        than being relative to it.

        """
        path = self.path
        if path:
            if self.is_local:
                # use posix path since it is supposed to be unix-style
                path = posixpath.join(self.datapackage_uri, path)
            else:
                path = urllib.parse.urljoin(self.datapackage_uri, path)
        return path

    @property
    def url(self):
        """The url of this data resource"""
        return self.descriptor.get('url', None)

    @url.setter
    def url(self, val):
        if not val and 'url' in self.descriptor:
            del self.descriptor['url']
            return

        if not is_url(val):
            raise ValueError("not a url: {}".format(val))

        self.descriptor['url'] = str(val)

        self.mediatype = self._guess_mediatype()
        self.format = self._guess_format()

    def _guess_mediatype(self):
        """Tries to guess the mediatype based off other properties of the
        resource. First, it will look at the path; if that does not
        exist, then it will try to guess it from the URL.

        """
        if self.path:
            mediatype, encoding = mimetypes.guess_type(self.path)
        elif self.url:
            mediatype, encoding = mimetypes.guess_type(self.url)
        else:
            mediatype = u''

        return str(mediatype)

    def _guess_format(self):
        """Tries to guess the format based off other properties of the
        resource. First, it will look at the path; if that does not
        exist, it will try to guess it from the URL; and if that does
        not exist, it will try to guess it from the mediatype.

        """
        if self.path:
            format = posixpath.splitext(self.path)[1][1:]
        elif self.url:
            path = urllib.parse.urlparse(self.url).path
            format = posixpath.splitext(path)[1][1:]
        else:
            format = mimetypes.guess_extension(self.mediatype)
            if format:
                format = format[1:]
            else:
                format = u''

        return str(format)

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

    @name.setter
    def name(self, val):
        if not val:
            val = u''
        elif not name_regex.match(val):
            raise ValueError(
                "name '{}' contains invalid characters".format(val))
        self.descriptor['name'] = val

    @property
    def format(self):
        """A format like 'csv', 'xls', 'json', etc. Would be expected to be
        the the standard file extension for this type of resource.

        """
        return self.descriptor.get('format', '')

    @format.setter
    def format(self, val):
        if not val:
            val = u''
        self.descriptor['format'] = str(val)

    @property
    def mediatype(self):
        """The mediatype/mimetype of the resource, e.g. 'text/csv',
        'application/vnd.ms-excel'.

        """
        return self.descriptor.get('mediatype', '')

    @mediatype.setter
    def mediatype(self, val):
        if not val:
            val = u''
        elif not is_mimetype(val):
            raise ValueError("not a valid mimetype: {}".format(val))
        self.descriptor['mediatype'] = str(val)
        self.format = self._guess_format()

    @property
    def encoding(self):
        """Specify the character encoding of a resource data file. The values
        should be one of the "Preferred MIME Names" for a character
        encoding registered with IANA. If no value for this key is
        specified then the default is UTF-8.

        """
        return self.descriptor.get('encoding', u'utf-8')

    @encoding.setter
    def encoding(self, val):
        if not val:
            val = u'utf-8'
        self.descriptor['encoding'] = str(val)

    @property
    def bytes(self):
        """The size of the file in bytes."""
        return self.descriptor.get('bytes', None)

    def _data_bytes(self):
        """Compute the size of the inline data"""
        if not self.data:
            raise ValueError("data is not specified")
        bytestr = str(json.dumps(self.data)).encode(self.encoding)
        return len(bytestr)

    def _path_bytes(self):
        """Compute the size of the file specified by the path"""
        if not self.path:
            raise ValueError("path to file is not specified")
        if self.is_local:
            size = os.path.getsize(self.fullpath)
        else:
            site = urllib.urlopen(self.fullpath)
            meta = site.info()
            size = int(meta.getheaders("Content-Length")[0])

        return size

    def _url_bytes(self):
        """Compute the size of the file specified by the url"""
        if not self.url:
            raise ValueError("url to file is not specified")
        site = urllib.urlopen(self.url)
        meta = site.info()
        size = int(meta.getheaders("Content-Length")[0])
        return size

    def update_bytes(self, verify=True):
        """Re-compute the size of the resource, using either the inline data,
        the path, or the url (whichever one exists first, in that
        order). If 'verify' is True and a size is already present in
        the descriptor, then this will check that the size hasn't
        changed, and throw an error if it has.

        """
        old_size = self.bytes
        if self.data:
            new_size = self._data_bytes()
        elif self.path:
            new_size = self._path_bytes()
        elif self.url:
            new_size = self._url_bytes()
        else:
            raise ValueError("resource not found")

        if verify and old_size and (old_size != new_size):
            raise RuntimeError(
                "size of file has changed! (was: {}, is now: {})".format(
                    old_size, new_size))

        self.descriptor['bytes'] = new_size

    @property
    def hash(self):
        """The MD5 hash for this resource."""
        return self.descriptor.get('hash', None)

    def _data_hash(self):
        """Computes the md5 checksum of the inline data."""
        bytestr = str(json.dumps(self.data)).encode(self.encoding)
        md5 = hashlib.md5()
        md5.update(bytestr)
        hash = md5.hexdigest()
        return hash

    def _path_hash(self):
        """Computes the md5 checksum of the file saved at the given path."""
        # we need to compute the md5 sum one chunk at a time, because
        # some files are too large to fit in memory
        if not self.path:
            raise ValueError("path to file is not specified")
        md5 = hashlib.md5()
        with self._open('rb') as fh:
            while True:
                chunk = fh.read(128)
                if not chunk:
                    break
                md5.update(chunk)
        hash = md5.hexdigest()
        return hash

    def _url_hash(self):
        """Computes the md5 checksum of the file saved at the url."""
        # probably want to download the data first and store it
        # somewhere before computing the MD5 sum otherwise it'll have
        # be downloaded twice. But then if that's the case then
        # _path_hash can probably just be used?
        raise NotImplementedError

    def update_hash(self, verify=True):
        old_hash = self.hash
        if self.data:
            new_hash = self._data_hash()
        elif self.path:
            new_hash = self._path_hash()
        elif self.url:
            new_hash = self._url_hash()
        else:
            raise ValueError("resource not found")

        if verify and old_hash and (old_hash != new_hash):
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

import os
import fnmatch
from setuptools import setup, find_packages
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def schema_files():
    '''Return all CSV and JSON files paths in datapackage/schemas

    The paths are relative to ./datapackage
    '''
    def recursive_glob(path, patterns):
        results = []
        for base, dirs, files in os.walk(path):
            matching_files = []
            for pattern in patterns:
                matching_files.extend(fnmatch.filter(files, pattern))
            results.extend(os.path.join(base, f) for f in matching_files)
        return results

    base_folder = 'datapackage'
    remove_base_folder = lambda path: path[len(base_folder) + 1:]

    path = os.path.join(base_folder, 'schemas')
    files_paths = recursive_glob(path, ['*.csv', '*.json'])

    return [remove_base_folder(f) for f in files_paths]


setup(
    name='datapackage',
    version='0.6.1',
    description=(
        'Utilities to work with Data Packages as defined on dataprotocols.org'
    ),
    long_description=long_description,

    url='https://github.com/okfn/datapackage-py',

    author='Open Knowledge Foundation',
    author_email='info@okfn.org',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='data dataprotocols jsontableschema frictionlessdata datascience',

    packages=find_packages(exclude=['tests']),
    package_data={'datapackage': schema_files()},

    install_requires=[
        'six >= 1.10.0',
        'requests >= 2.8.0',
        'jsonschema >= 2.5.1',
        'tabulator >= 0.4.0',
        'jsontableschema >= 0.5.1',
        'unicodecsv>=0.14',
    ],
)

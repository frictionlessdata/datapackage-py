#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import io
import os
import fnmatch

from setuptools import setup, find_packages

description = "A Python library for working with a Data Package Registry."
with io.open('README.md') as readme:
    long_description = ''.join(
        filter(lambda x: 'https://travis-ci.org/' not in x,
               readme.readlines()))

dependencies = [
    'requests>=2.8.0',
    'six>=1.10.0',
]


def schema_files():
    '''Return all CSV and JSON files paths in datapackage_registry/schemas

    The paths are relative to ./datapackage_registry
    '''
    def recursive_glob(path, patterns):
        results = []
        for base, dirs, files in os.walk(path):
            matching_files = []
            for pattern in patterns:
                matching_files.extend(fnmatch.filter(files, pattern))
            results.extend(os.path.join(base, f) for f in matching_files)
        return results

    base_folder = 'datapackage_registry'
    remove_base_folder = lambda path: path[len(base_folder) + 1:]

    path = os.path.join(base_folder, 'schemas')
    files_paths = recursive_glob(path, ['*.csv', '*.json'])

    return [remove_base_folder(f) for f in files_paths]

setup(
    name='datapackage-registry',
    version='0.2.0',
    url='https://github.com/okfn/datapackage-registry-py',
    license='MIT',
    description=description,
    long_description=long_description,
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_dir={'datapackage_registry': 'datapackage_registry'},
    package_data={'datapackage_registry': schema_files()},
    install_requires=dependencies,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)

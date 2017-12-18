# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
from setuptools import setup, find_packages


# Helpers
def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding='utf-8').read().strip()
    return contents


# Prepare
PACKAGE = 'datapackage'
NAME = PACKAGE.replace('_', '-')
INSTALL_REQUIRES = [
    'six>=1.10,<2.0',
    'click>=6.7,<7.0',
    'requests>=2.8,<3.0',
    'cchardet>=1.0,<2.0',
    'jsonschema>=2.5,<3.0',
    'unicodecsv>=0.14,<2.0',
    'jsonpointer>=1.10,<2.0',
    'tableschema>=1.0.7,<2.0',
    'tabulator>=1.3,<2.0',
]
TESTS_REQUIRE = [
    'pylama',
    'tox',
]
README = read('README.md')
VERSION = read(PACKAGE, 'VERSION')
PACKAGES = find_packages(exclude=['examples', 'tests'])


# Run
setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={'develop': TESTS_REQUIRE},
    entry_points={
        'console_scripts': [
            'datapackage = datapackage.cli:cli',
        ]
    },
    zip_safe=False,
    long_description=README,
    description='Utilities to work with Data Packages as defined on specs.frictionlessdata.io',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='https://github.com/frictionlessdata/datapackage-py',
    license='MIT',
    keywords=[
        'frictionless data',
        'open data',
        'json schema',
        'table schema',
        'data package',
        'tabular data package',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import io

from setuptools import setup, find_packages

description = "A Python library to validate Data Package datapackage.json files."
with io.open('README.md') as readme:
    long_description = ''.join(
        filter(lambda x: 'https://travis-ci.org/' not in x,
               readme.readlines()))

setup(
    name='datapackage-validate',
    version='0.0.1',
    url='https://github.com/okfn/datapackage-validate-py',
    license='MIT',
    description=description,
    long_description=long_description,
    maintainer='Brook Elgie',
    maintainer_email='brook.elgie@okfn.org',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_dir={'datapackage_validate': 'datapackage_validate'},
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
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)

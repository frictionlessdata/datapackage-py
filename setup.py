#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

description = "Manage and load dataprotocols.org Data Packages"
with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name = 'datapackage',
    version = '0.3.1',
    url = 'https://github.com/tryggvib/datapackage',
    license = 'GPLv3',
    description = description,
    long_description = long_description,
    maintainer = 'Tryggvi Björgvinsson',
    maintainer_email = 'tryggvi.bjorgvinsson@okfn.org',
    packages = ['datapackage'],
    package_dir={'datapackage': 'datapackage'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)

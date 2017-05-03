import os
import fnmatch
from setuptools import setup, find_packages
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='datapackage',
    version='1.0.0-alpha4',
    description=(
        'Utilities to work with Data Packages as defined on specs.frictionlessdata.io'
    ),
    long_description=long_description,

    url='https://github.com/frictionlessdata/datapackage-py',

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

    keywords='data tableschema frictionlessdata datascience',

    packages=find_packages(exclude=['tests']),
    include_package_data=True,

    install_requires=[
        'six>=1.10,<2.0a',
        'requests>=2.8,<3.0a',
        'jsonschema>=2.5,<3.0a',
        'unicodecsv>=0.14,<1.0a',
        'jsontableschema>=0.8,<1.0a',
        'tableschema>=1.0.0a4,<2.0',
        'tabulator>=0.14.2,<1.0a',
        'jsonpointer>=1.10,<2.0a',
    ],
)

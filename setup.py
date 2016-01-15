from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='datapackage',
    version='0.0.1',
    description=(
        'Utilities to work with Data Packages as defined on dataprotocols.org'
    ),
    long_description=long_description,

    url='https://github.com/okfn/datapackage-py',

    author='Open Knowledge Foundation',
    author_email='info@okfn.org',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='data dataprotocols jsontableschema openrefine datascience',

    packages=find_packages(exclude=['tests']),

    install_requires=[
        'six >= 1.10.0',
        'datapackage_validate >= 0.3.1',
        'tabulator',
    ],

    dependency_links=[
        'https://github.com/okfn/tabulator-py/tarball/master#egg=tabulator'
    ],
)

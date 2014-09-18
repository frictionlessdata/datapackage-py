Module documentation
====================

Main module
-----------

For most uses the main module ``datapackage.datapackage`` which includes the ``DataPackage`` class is what users will need to know about. The class can also be imported directly from ``datapackage``::

    from datapackage import DataPackage

.. automodule:: datapackage.datapackage
   :members:

Helper classes
--------------

To help with creation of data packages ``datapackage`` includes a few helper classes which aid construction of data package hashes. These come in five modules: ``datapackage.resource`` (includes ``Resource`` class which can also be imported directly from ``datapackage`` just like ``DataPackage``), ``datapackage.schema``, ``datapackage.licenses``, ``datapackage.sources`` and ``datapackage.persons``.

Each of these includes various amount of helper classes. ``datapackage.schema`` is notable for containing most helper classes (since constructing a schema requires quite a lot of hashes).

.. automodule:: datapackage.resource
   :members:

.. automodule:: datapackage.schema
   :members:

.. automodule:: datapackage.licenses
   :members:

.. automodule:: datapackage.sources
   :members:

.. automodule:: datapackage.persons
   :members:

Helper module
-------------

``datapackage`` includes a utils helper module ``datapackage.util`` which provides a few helper methods to make working with data packages (and life in general) easier.

.. automodule:: datapackage.util
   :members:


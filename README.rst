datapackage
===========

**datapackage** provides means to work with DataPackages as defined on
`dataprotocols.org <http://dataprotocols.org/data-packages/>`__.

::

    >> import datapackage
    >>
    >> # Note trailing slash is important for data.okfn.org
    >> datapkg = datapackage.DataPackage('http://data.okfn.org/data/cpi/')
    >>
    >> print datapkg.title
    Annual Consumer Price Index (CPI)
    >> print datapkg.description
    Annual Consumer Price Index (CPI) for most countries in the world. Reference year is 2005.
    >> # Weird example just to show how to work with data rows
    >> print sum([row['CPI'] for row in datapkg.data])
    668134.635662

Python support
--------------

**datapackage** supports both Python 2 and 3.

License
-------

datapackage is available under the GNU General Public License, version
3. See LICENCE for more details.

# DataPackage.py

[![Build Status](https://travis-ci.org/okfn/datapackage-py.svg)](https://travis-ci.org/okfn/datapackage-py)
[![Test Coverage](https://coveralls.io/repos/okfn/datapackage-py/badge.svg?branch=master&service=github)](https://coveralls.io/github/okfn/datapackage-py)
[![Documentation](https://readthedocs.org/projects/datapackagepy/badge/?version=latest)](https://datapackagepy.readthedocs.org/en/latest/)
![Support Python versions 2.7, 3.3, 3.4 and 3.5](https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5-blue.svg)

A model for working with [Data Packages].

  [Data Packages]: http://dataprotocols.org/data-packages/

## Example

```python
import datapackage

dp = datapackage.DataPackage('http://data.okfn.org/data/core/gdp')
brazil_gdp = [{'Year': int(row['Year']), 'Value': float(row['Value'])}
              for row in dp.resources[0].data if row['Country Code'] == 'BRA']

max_gdp = max(brazil_gdp, key=lambda x: x['Value'])
min_gdp = min(brazil_gdp, key=lambda x: x['Value'])
percentual_increase = max_gdp['Value'] / min_gdp['Value']

msg = (
    'The highest Brazilian GDP occured in {max_gdp_year}, when it peaked at US$ '
    '{max_gdp:1,.0f}. This was {percentual_increase:1,.2f}% more than its '
    'minimum GDP in {min_gdp_year}.'
).format(max_gdp_year=max_gdp['Year'],
         max_gdp=max_gdp['Value'],
         percentual_increase=percentual_increase,
         min_gdp_year=min_gdp['Year'])

print(msg)
# The highest Brazilian GDP occured in 2011, when it peaked at US$ 2,615,189,973,181. This was 172.44% more than its minimum GDP in 1960.
```

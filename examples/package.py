from datapackage import Package

# Init
package = Package()

# Infer
package.infer('**/*.csv')
print(package.descriptor)

# Tweak
package.descriptor['resources'][1]['schema']['fields'][1]['type'] = 'year'
package.commit()
print(package.valid) # true

# Read
print(package.get_resource('population').read(keyed=True))
#[ { city: 'london', year: 2017, population: 8780000 },
#  { city: 'paris', year: 2017, population: 2240000 },
#  { city: 'rome', year: 2017, population: 2860000 } ]

# Save
package.save('tmp/datapackage.zip')

# Load
package = Package('tmp/datapackage.zip', base_path='tmp')
print(package.descriptor)

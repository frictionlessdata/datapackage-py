from datapackage import Resource

# Create
resource = Resource({'path': 'data/data.csv'})
resource.tabular # true
resource.headers # ['city', 'location']
print(resource.read(keyed=True))
# [
#   {city: 'london', location: '51.50,-0.11'},
#   {city: 'paris', location: '48.85,2.30'},
#   {city: 'rome', location: 'N/A'},
# ]

# Infer
resource.infer()
print(resource.descriptor)
#{ path: 'data.csv',
#  profile: 'tabular-data-resource',
#  encoding: 'utf-8',
#  name: 'data',
#  format: 'csv',
#  mediatype: 'text/csv',
# schema: { fields: [ [Object], [Object] ], missingValues: [ '' ] } }
# resource.read(keyed=True)
# Fails with a data validation error

# Tweak
resource.descriptor['schema']['missingValues'] = 'N/A'
resource.commit()
resource.valid # False
print(resource.errors)
# Error: Descriptor validation error:
#   Invalid type: string (expected array)
#    at "/missingValues" in descriptor and
#    at "/properties/missingValues/type" in profile

# Tweak-2
resource.descriptor['schema']['missingValues'] = ['', 'N/A']
resource.commit()
print(resource.valid) # true

# Read
print(resource.read(keyed=True))
# [
#   {city: 'london', location: [51.50,-0.11]},
#   {city: 'paris', location: [48.85,2.30]},
#   {city: 'rome', location: null},
# ]

# Save
resource.save('tmp/dataresource.json')

# Open
resource = Resource('tmp/dataresource.json', base_path='tmp')
print(resource)

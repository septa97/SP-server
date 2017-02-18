import os
import requests
import json

# Function that retrieves the slugs of all the courses in the Coursera Catalog API
# Input: N/A
# Output: N/A
def start():
	data = requests.get('https://api.coursera.org/api/courses.v1?start=0&limit=100').json()
	slugs = {'elements': []}
	for element in data['elements']:
		slugs['elements'].append(element['slug'])

	while (data['paging'].get('next') != None):
		data = requests.get('https://api.coursera.org/api/courses.v1?start=' + data['paging']['next'] + '&limit=100').json()
		for element in data['elements']:
			slugs['elements'].append(element['slug'])

	dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../data';
	os.makedirs(dir_path, exist_ok=True)
	with open(dir_path + '/slugs.json', 'w') as fp:
		json.dump(slugs, fp)

	print('Slugs are written to slugs.json...')

start()

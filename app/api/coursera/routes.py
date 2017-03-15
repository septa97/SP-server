import json
import requests
import os
from flask import Blueprint, jsonify

# This blueprint is a wrapper for calling the Coursera Catalog API
courses_URL = 'https://api.coursera.org/api/courses.v1'
partners_URL = 'https://api.coursera.org/api/partners.v1'
instructors_URL = 'https://api.coursera.org/api/instructors.v1'

mod = Blueprint('coursera', __name__)


@mod.route('/courses', methods=['GET'])
def get_all_courses():
	"""
	Retrieves all the courses and their fields
	"""
	fields = ','.join(['id', 'slug', 'courseType', 'name', 'primaryLanguages',
						'subtitleLanguages', 'partnerLogo', 'instructorIds', 'partnerIds',
						'photoUrl', 'certificates', 'description', 'startDate', 'workload',
						'previewLink', 'specializations', 's12nIds', 'domainTypes', 'categories'])

	data = {'elements': []}

	res = requests.get(courses_URL + '?fields=' + fields + '&start=0&limit=100').json()
	data['elements'].extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(courses_URL + '?fields=' + fields + '&start=' + res['paging']['next'] + '&limit=100').json()
		data['elements'].extend(res['elements'])

	return jsonify(data)

@mod.route('/instructors', methods=['GET'])
def get_all_instructors():
	"""
	Retrieves all the instructors and their fields
	"""
	fields = ','.join(['id', 'photo', 'photo150', 'bio', 'prefixName', 'firstName', 'middleName',
						'lastName', 'suffixName', 'fullName', 'title', 'department', 'website',
						'websiteTwitter', 'websiteFacebook', 'websiteLinkedin', 'websiteGplus', 'shortName'])

	data = {'elements': []}

	res = requests.get(instructors_URL + '?fields=' + fields + '&start=0&limit=100').json()
	data['elements'].extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(instructors_URL + '?fields=' + fields + '&start=' + res['paging']['next'] + '&limit=100').json()
		data['elements'].extend(res['elements'])

	return jsonify(data)

@mod.route('/partners', methods=['GET'])
def get_all_partners():
	"""
	Retrieves all the partners and their fields
	"""
	fields = ','.join(['id', 'name', 'shortName', 'description', 'banner', 'courseIds', 'instructorIds',
						'primaryColor', 'logo', 'squareLogo', 'rectangularLogo', 'links', 'location'])

	data = {'elements': []}

	res = requests.get(partners_URL + '?fields=' + fields + '&start=0&limit=100').json()
	data['elements'].extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(partners_URL + '?fields=' + fields + '&start=' + res['paging']['next'] + '&limit=100').json()
		data['elements'].extend(res['elements'])

	return jsonify(data)

@mod.route('/partners/location', methods=['GET'])
def get_all_partners_location():
	"""
	Retrieves all the partner locations
	"""
	data = {'elements': []}

	res = requests.get(partners_URL + '?fields=location&start=0&limit=100').json()
	data['elements'].extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(partners_URL + '?fields=location&start=' + res['paging']['next'] + '&limit=100').json()
		data['elements'].extend(res['elements'])

	return jsonify(data)

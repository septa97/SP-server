import json
import requests
import os
import rethinkdb as r

from flask import Blueprint, jsonify
from rethinkdb.errors import RqlRuntimeError
from app.configuration.config import config
from app.lib.rethinkdb_connect import connection
from app.utils.rethinkdb_helpers import create_or_delete_table


# This blueprint is a wrapper for calling the Coursera Catalog API
courses_URL = 'https://api.coursera.org/api/courses.v1'
partners_URL = 'https://api.coursera.org/api/partners.v1'
instructors_URL = 'https://api.coursera.org/api/instructors.v1'

mod = Blueprint('coursera', __name__)

@mod.route('/save_courses', methods=['GET'])
def save_all_courses():
	"""
	Retrieves all the courses and their fields directly from the Coursera Catalog API and saves it to the RethinkDB server
	"""
	fields = ','.join(['id', 'slug', 'courseType', 'name', 'primaryLanguages',
						'subtitleLanguages', 'partnerLogo', 'instructorIds', 'partnerIds',
						'photoUrl', 'certificates', 'description', 'startDate', 'workload',
						'previewLink', 'specializations', 's12nIds', 'domainTypes', 'categories'])

	courses = []

	res = requests.get(courses_URL + '?fields=' + fields + '&start=0&limit=100').json()
	courses.extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(courses_URL + '?fields=' + fields + '&start=' + res['paging']['next'] + '&limit=100').json()
		courses.extend(res['elements'])

	create_or_delete_table('courses', delete=True)
	r.table('courses').insert(courses).run(connection)
	print('Successfully inserted all the courses.')

	return jsonify({'message': 'Successfully inserted all the courses.'})


@mod.route('/save_instructors', methods=['GET'])
def save_all_instructors():
	"""
	Retrieves all the instructors and their fields directly from the Coursera Catalog API and saves it to the RethinkDB server
	"""
	fields = ','.join(['id', 'photo', 'photo150', 'bio', 'prefixName', 'firstName', 'middleName',
						'lastName', 'suffixName', 'fullName', 'title', 'department', 'website',
						'websiteTwitter', 'websiteFacebook', 'websiteLinkedin', 'websiteGplus', 'shortName'])

	instructors = []

	res = requests.get(instructors_URL + '?fields=' + fields + '&start=0&limit=100').json()
	instructors.extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(instructors_URL + '?fields=' + fields + '&start=' + res['paging']['next'] + '&limit=100').json()
		instructors.extend(res['elements'])

	create_or_delete_table('instructors', delete=True)
	r.table('instructors').insert(instructors).run(connection)
	print('Successfully inserted all the instructors.')

	return jsonify({'message': 'Successfully inserted all the instructors.'})


@mod.route('/save_partners', methods=['GET'])
def save_all_partners():
	"""
	Retrieves all the partners and their fields directly from the Coursera Catalog API and saves it to the RethinkDB server
	"""
	fields = ','.join(['id', 'name', 'shortName', 'description', 'banner', 'courseIds', 'instructorIds',
						'primaryColor', 'logo', 'squareLogo', 'rectangularLogo', 'links', 'location'])

	partners = []

	res = requests.get(partners_URL + '?fields=' + fields + '&start=0&limit=100').json()
	partners.extend(res['elements'])

	while (res['paging'].get('next') != None):
		res = requests.get(partners_URL + '?fields=' + fields + '&start=' + res['paging']['next'] + '&limit=100').json()
		partners.extend(res['elements'])

	create_or_delete_table('partners', delete=True)
	r.table('partners').insert(partners).run(connection)
	print('Successfully inserted all the partners.')

	return jsonify({'message': 'Successfully inserted all the partners.'})


@mod.route('/partner/<partner_id>/courses', methods=['GET'])
def get_all_courses_offered(partner_id):
	"""
	Retrieves all the courses offered by an institution/partner
	"""
	data = {'courses': []}

	res = requests.get(partners_URL + '/' + partner_id + '?includes=courseIds').json()
	data['courses'].extend(res['linked']['courses.v1'])

	return jsonify(data)

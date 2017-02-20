import json
import requests
from flask import Blueprint, jsonify

# This blueprint is a wrapper for calling the Coursera Catalog API
courses_URL = 'https://api.coursera.org/api/courses.v1'
partners_URL = 'https://api.coursera.org/api/partners.v1'
instructors_URL = 'https://api.coursera.org/api/instructors.v1'

mod = Blueprint('coursera', __name__)

@mod.route('/partners/location', methods=['GET'])
def get_all_reviews():
	return jsonify(requests.get(partners_URL + '?fields=location').json())

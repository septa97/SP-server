import rethinkdb as r

from flask import Blueprint, jsonify
from nltk.corpus import sentiwordnet as swn
from pydash.collections import count_by
from textblob import TextBlob

from app.lib.rethinkdb_connect import connection
from app.modules.features import FeaturePreprocessor
from app.modules.preprocessor import preprocess, is_English
from app.modules.vocabulary import create_vocabulary_list
from app.modules.labeller import Labeller


mod = Blueprint('rethinkdb', __name__)

@mod.route('/reviews', methods=['GET'])
def get_all_reviews():
	"""
	Retrieves all the reviews from the RethinkDB server
	"""
	cursor = r.table('reviews').run(connection)
	reviews = []

	for document in cursor:
		reviews.extend(document['data'])

	return jsonify(reviews)


@mod.route('/courses', methods=['GET'])
def get_all_courses():
	"""
	Retrieves all the courses and their fields from the current data stored on RethinkDB server
	"""
	data = {'courses': []}

	cursor = r.table('courses').run(connection)

	for document in cursor:
		data['courses'].append(document)

	return jsonify(data)


@mod.route('/instructors', methods=['GET'])
def get_all_instructors():
	"""
	Retrieves all the instructors and their fields from the current data stored on RethinkDB server
	"""
	data = {'instructors': []}

	cursor = r.table('instructors').run(connection)

	for document in cursor:
		data['instructors'].append(document)

	return jsonify(data)


@mod.route('/partners', methods=['GET'])
def get_all_partners():
	"""
	Retrieves all the partners and their fields from the current data stored on RethinkDB server
	"""
	data = {'partners': []}

	cursor = r.table('partners').run(connection)

	for document in cursor:
		data['partners'].append(document)

	return jsonify(data)


@mod.route('/partners/location', methods=['GET'])
def get_all_partners_location():
	"""
	Retrieves all the partner locations from the RethinkDB server
	"""
	data = {'elements': []}

	cursor = r.table('partners').pluck('id', 'location', 'name').run(connection)

	for document in cursor:
		data['elements'].append(document)

	return jsonify(data)


@mod.route('/course/<slug>/reviews-and-ratings', methods=['GET'])
def get_all_course_reviews(slug):
	"""
	Retrieves all the course review of a specific course based on their <slug>
	"""
	data = {
		'reviews_and_ratings': []
	}

	cursor = r.table('reviews').filter({
			'id': slug
		}).run(connection)

	for document in cursor:
		for i in range(0, len(document['data'])):
			data['reviews_and_ratings'].append({
					'review': document['data'][i],
					'rating': document['ratings'][i]
				})

	cursor = r.table('courses').filter({
			'slug': slug
		}).pluck('name').run(connection)

	for document in cursor:
		data['course_name'] = document['name']

	return jsonify(data)


@mod.route('/courses/domain_types', methods=['GET'])
def get_all_courses_domain_types():
	"""
	Retrieves all the unique domain types (domainId and subdomainId) acroll all the courses
	"""
	data = {
		'domainIds': [],
		'subdomainIds': []
	}

	cursor = r.table('courses').pluck('domainTypes').run(connection)

	for document in cursor:
		for domain_type in document['domainTypes']:
			# Add the domainId if not yet in the list
			if domain_type['domainId'] not in data['domainIds']:
				data['domainIds'].append(domain_type['domainId'])

			# Add the subdomainId if not yet in the list
			if domain_type['subdomainId'] not in data['subdomainIds']:
				data['subdomainIds'].append(domain_type['subdomainId'])

	return jsonify(data)


@mod.route('/courses/domain_id/<domain_id>', methods=['GET'])
def get_all_courses_domain_id(domain_id):
	"""
	Retrieves all the courses with the specified <domain_id>
	"""
	data = {'courses': []}

	cursor = r.table('courses').filter(r.row['domainTypes'].contains(lambda e:
			e['domainId'].eq(domain_id)
		)).run(connection)

	for document in cursor:
		data['courses'].append(document)

	return jsonify(data)


@mod.route('/courses/subdomain_id/<subdomain_id>', methods=['GET'])
def get_all_courses_subdomain_id(subdomain_id):
	"""
	Retrieves all the courses with the specified <subdomain_id>
	"""
	data = {'courses': []}

	cursor = r.table('courses').filter(r.row['domainTypes'].contains(lambda e:
			e['subdomainId'].eq(subdomain_id)
		)).run(connection)

	for document in cursor:
		data['courses'].append(document)

	return jsonify(data)


@mod.route('/courses/domain_id_and_or_subdomain_id/<domain_id>/<subdomain_id>/<both>/reviews-and-ratings', methods=['GET'])
def get_all_course_reviews_domain_id_subdomain_id(domain_id, subdomain_id, both):
	"""
	Retrieves all the course reviews with the specified <domain_id> and/or <subdomain_id>
	"""
	data = {
		'reviews_and_ratings': [],
		'courses': []
	}

	cursor = r.table('courses').filter(r.row['domainTypes'].contains(lambda e:
			(e['domainId'].eq(domain_id) & e['subdomainId'].eq(subdomain_id)) if both == 'True' else
			(e['domainId'].eq(domain_id) | e['subdomainId'].eq(subdomain_id))
		)).run(connection)

	for document in cursor:
		reviews_cursor = r.table('reviews').filter({
				'id': document['slug']
			}).run(connection)

		for reviews_document in reviews_cursor:
			for i in range(0, len(reviews_document['data'])):
				if not is_English(reviews_document['data'][i]):
					continue

				data['reviews_and_ratings'].append({
						'review': reviews_document['data'][i],
						'rating': reviews_document['ratings'][i]
					})

		data['courses'].append(document['name'])

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/overall', methods=['GET'])
def get_all_course_review_words_overall(course_slug):
	"""
	Retrieves all the preprocessed words
	"""
	data = {}

	cursor = r.table('reviews').filter({
				'id': course_slug
			}).run(connection)

	reviews = []
	for document in cursor:
		reviews.extend(document['data'])

	if len(reviews) == 0:
		return jsonify(data)

	words = []
	for review in reviews:
		tokens = preprocess(review)

		if tokens == -1:
			continue

		words.extend(tokens)

	data['word_mapping'] = count_by(words)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/positive', methods=['GET'])
def get_all_course_review_words_positive(course_slug):
	"""
	Retrieves all the preprocessed positive words
	"""
	data = {}

	cursor = r.table('reviews').filter({
				'id': course_slug
			}).run(connection)

	reviews = []
	for document in cursor:
		reviews.extend(document['data'])

	if len(reviews) == 0:
		return jsonify(data)

	overall_words = []
	for review in reviews:
		tokens = preprocess(review)

		if tokens == -1:
			continue

		# Check each word if positive
		words = []
		for word in tokens:
			tb = TextBlob(word)

			if tb.sentiment.subjectivity != 0 and tb.sentiment.polarity > 0:
				words.append(word)

		overall_words.extend(words)

	data['word_mapping'] = count_by(overall_words)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/negative', methods=['GET'])
def get_all_course_review_words_negative(course_slug):
	"""
	Retrieves all the preprocessed negative words
	"""
	data = {}

	cursor = r.table('reviews').filter({
				'id': course_slug
			}).run(connection)

	reviews = []
	for document in cursor:
		reviews.extend(document['data'])

	if len(reviews) == 0:
		return jsonify(data)

	overall_words = []
	for review in reviews:
		tokens = preprocess(review)

		if tokens == -1:
			continue

		# Check each word if negative
		words = []
		for word in tokens:
			tb = TextBlob(word)

			if tb.sentiment.subjectivity != 0 and tb.sentiment.polarity < 0:
				words.append(word)

		overall_words.extend(words)

	data['word_mapping'] = count_by(overall_words)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/neutral', methods=['GET'])
def get_all_course_review_words_neutral(course_slug):
	"""
	Retrieves all the preprocessed neutral words
	"""
	data = {}

	cursor = r.table('reviews').filter({
				'id': course_slug
			}).run(connection)

	reviews = []
	for document in cursor:
		reviews.extend(document['data'])

	if len(reviews) == 0:
		return jsonify(data)

	overall_words = []
	for review in reviews:
		tokens = preprocess(review)

		if tokens == -1:
			continue

		# Check each word if neutral
		words = []
		for word in tokens:
			tb = TextBlob(word)

			if tb.sentiment.subjectivity == 0 or tb.sentiment.polarity == 0:
				words.append(word)

		overall_words.extend(words)

	data['word_mapping'] = count_by(overall_words)

	return jsonify(data)

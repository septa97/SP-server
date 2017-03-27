import rethinkdb as r

from flask import Blueprint, jsonify
from nltk.corpus import sentiwordnet as swn

from app.configuration.config import config
from app.lib.rethinkdb_connect import connection
from app.modules.features import FeaturePreprocessor
from app.modules.preprocessor import preprocess
from app.modules.vocabulary import create_vocabulary_list


mod = Blueprint('rethinkdb', __name__)

@mod.route('/reviews', methods=['GET'])
def get_all_reviews():
	"""
	Retrieves all the reviews from the RethinkDB server
	"""
	cursor = r.db(config['DB_NAME']).table('reviews').run(connection)
	reviews = []
	rows = []

	for document in cursor:
		rows.append(document)

	for row in rows:
		slug = list(filter(lambda k: k != 'id', row.keys()))[0]
		reviews.extend(row[slug])

	return jsonify(reviews)


@mod.route('/courses', methods=['GET'])
def get_all_courses():
	"""
	Retrieves all the courses and their fields from the current data stored on RethinkDB server
	"""
	data = {'courses': []}

	cursor = r.db(config['DB_NAME']).table('courses').run(connection)

	for document in cursor:
		data['courses'].append(document)

	return jsonify(data)


@mod.route('/instructors', methods=['GET'])
def get_all_instructors():
	"""
	Retrieves all the instructors and their fields from the current data stored on RethinkDB server
	"""
	data = {'instructors': []}

	cursor = r.db(config['DB_NAME']).table('instructors').run(connection)

	for document in cursor:
		data['instructors'].append(document)

	return jsonify(data)


@mod.route('/partners', methods=['GET'])
def get_all_partners():
	"""
	Retrieves all the partners and their fields from the current data stored on RethinkDB server
	"""
	data = {'partners': []}

	cursor = r.db(config['DB_NAME']).table('partners').run(connection)

	for document in cursor:
		data['partners'].append(document)

	return jsonify(data)


@mod.route('/partners/location', methods=['GET'])
def get_all_partners_location():
	"""
	Retrieves all the partner locations from the RethinkDB server
	"""
	data = {'elements': []}

	cursor = r.db(config['DB_NAME']).table('partners').pluck('id', 'location', 'name').run(connection)

	for document in cursor:
		data['elements'].append(document)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/overall', methods=['GET'])
def get_all_course_review_words_overall(course_slug):
	"""
	Retrieves all the preprocessed words
	"""
	data = {'words': []}

	cursor = r.db(config['DB_NAME']).table('reviews').filter({
			'id': course_slug
		}).run(connection)

	row = []
	for document in cursor:
		row.append(document)

	if (len(row) == 0):
		return jsonify(data)

	slug = list(filter(lambda k: k != 'id', row[0].keys()))[0]
	reviews = row[0][slug]

	for review in reviews:
		tokens = preprocess(review)

		if (tokens == -1):
			continue

		data['words'].extend(tokens)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/positive', methods=['GET'])
def get_all_course_review_words_positive(course_slug):
	"""
	Retrieves all the preprocessed positive words
	"""
	data = {'words': []}

	cursor = r.db(config['DB_NAME']).table('reviews').filter({
			'id': course_slug
		}).run(connection)

	row = []
	for document in cursor:
		row.append(document)

	if (len(row) == 0):
		return jsonify(data)

	slug = list(filter(lambda k: k != 'id', row[0].keys()))[0]
	reviews = row[0][slug]

	for review in reviews:
		tokens = preprocess(review)

		if (tokens == -1):
			continue

		# Check each word if positive
		words = []
		for word in tokens:
			synset_list = list(swn.senti_synsets(word))

			if (len(synset_list) == 0):
				continue

			score = 0
			for synset in synset_list:
				score += (synset.pos_score() - synset.neg_score())

			if (score > 0):
				words.append(word)

		data['words'].extend(words)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/negative', methods=['GET'])
def get_all_course_review_words_negative(course_slug):
	"""
	Retrieves all the preprocessed negative words
	"""
	data = {'words': []}

	cursor = r.db(config['DB_NAME']).table('reviews').filter({
			'id': course_slug
		}).run(connection)

	row = []
	for document in cursor:
		row.append(document)

	if (len(row) == 0):
		return jsonify(data)

	slug = list(filter(lambda k: k != 'id', row[0].keys()))[0]
	reviews = row[0][slug]

	for review in reviews:
		tokens = preprocess(review)

		if (tokens == -1):
			continue

		# Check each word if negative
		words = []
		for word in tokens:
			synset_list = list(swn.senti_synsets(word))

			if (len(synset_list) == 0):
				continue

			score = 0
			for synset in synset_list:
				score += (synset.pos_score() - synset.neg_score())

			if (score < 0):
				words.append(word)

		data['words'].extend(words)

	return jsonify(data)


@mod.route('/course/<course_slug>/reviews/preprocessed-words/neutral', methods=['GET'])
def get_all_course_review_words_neutral(course_slug):
	"""
	Retrieves all the preprocessed neutral words
	"""
	data = {'words': []}

	cursor = r.db(config['DB_NAME']).table('reviews').filter({
			'id': course_slug
		}).run(connection)

	row = []
	for document in cursor:
		row.append(document)

	if (len(row) == 0):
		return jsonify(data)

	slug = list(filter(lambda k: k != 'id', row[0].keys()))[0]
	reviews = row[0][slug]

	for review in reviews:
		tokens = preprocess(review)

		if (tokens == -1):
			continue

		# Check each word if neutral
		words = []
		for word in tokens:
			synset_list = list(swn.senti_synsets(word))

			if (len(synset_list) == 0):
				continue

			objectivity_score = 0
			for synset in synset_list:
				objectivity_score += synset.obj_score()

			if (objectivity_score/len(synset_list) >= 0.875):
				words.append(word)

		data['words'].extend(words)

	return jsonify(data)


@mod.route('/extract-vocab/<int:vocab_size>', methods=['GET'])
def extract_vocab(vocab_size):
	"""
	Extracts the top vocab_size vocabularies
	"""
	cursor = r.db(config['DB_NAME']).table('reviews').run(connection)

	rows = []
	reviews = []

	for document in cursor:
		rows.append(document)

	for row in rows:
		slug = list(filter(lambda k: k != 'id', row.keys()))[0]
		reviews.extend(row[slug])

	create_vocabulary_list(reviews, vocab_size)

	return jsonify({'message': 'Successfully extracted the top ' + str(vocab_size) + ' vocabularies.'})


@mod.route('/extract-features/<int:vocab_size>', methods=['GET'])
def extract_features(vocab_size):
	"""
	Extracts the features of all the reviews
	"""
	feature_preprocessor = FeaturePreprocessor(vocab_size)
	num_of_english_reviews = feature_preprocessor.start(use_existing_vocab=True)

	return jsonify({'message': 'Successfully extracted the features of ' + str(num_of_english_reviews) + ' English reviews.'})

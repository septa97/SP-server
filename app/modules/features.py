import sys
import os
import rethinkdb as r
import numpy as np

from rethinkdb.errors import RqlRuntimeError
from nltk.corpus import sentiwordnet as swn

from app.configuration.config import config
from app.lib.rethinkdb_connect import connection
from app.modules.preprocessor import preprocess
from app.modules.vocabulary import create_vocabulary_list


class FeaturePreprocessor:
	def __init__(self, vocab_size):
		self.n = vocab_size
		self.reviews = []
		self.vocab_list = []
		self.init_connection()


	def start(self, use_existing_vocab=True):
		"""
		Retrieves all the reviews
		"""
		cursor = r.db(config['DB_NAME']).table('reviews').run(connection)
		rows = []

		for document in cursor:
			rows.append(document)

		for row in rows:
			slug = list(filter(lambda k: k != 'id', row.keys()))[0]
			self.reviews.extend(row[slug])

		if not use_existing_vocab:
			create_vocabulary_list(self.reviews, self.n)

		# Retrieve all the vocab rows
		cursor = r.db(config['DB_NAME']).table('vocab').filter({
			'size': self.n
		}).run(connection)

		for document in cursor:
			self.vocab_list = document[str(self.n)]

		return self.extract_features_and_labels()


	def init_connection(self):
		"""
		Initializes the connection to the RethinkDB server
		"""
		try:
			r.db(config['DB_NAME']).table_create('vocab').run(connection)
			print('Table vocab has been created.')
		except RqlRuntimeError:
			print('Table vocab already exists.')


	def extract_features_and_labels(self):
		"""
		Extracts the features of a list of reviews
		"""
		X = np.empty([0, self.n])
		y = np.array([])

		num = 0
		for i, review in zip(range(0, len(self.reviews)), self.reviews):
			print(i*100//len(self.reviews) , '%', end='\r')
			tokens = preprocess(review)

			# If the language of the review is not English
			if (tokens == -1):
				continue

			word_indices = self.get_word_indices(tokens)
			classification = self.identify_class(tokens)

			if (classification == 'no senti synsets'):
				continue

			num += 1
			feature_vector = self.get_feature_vector(word_indices)
			X = np.append(X, [feature_vector], axis=0)

			y = np.append(y, classification)

		print('Processed a total of', num, 'rows.')

		try:
			r.db(config['DB_NAME']).table_create('X').run(connection)
			print('X table has been created.')
		except RqlRuntimeError:
			print('Table X already exists. Deleting all rows...')
			r.db(config['DB_NAME']).table('X').delete().run(connection)
			print('All X rows are deleted.')

		try:
			r.db(config['DB_NAME']).table_create('y').run(connection)
			print('y table has been created.')
		except RqlRuntimeError:
			print('Table y already exists. Deleting all rows...')
			r.db(config['DB_NAME']).table('y').delete().run(connection)
			print('All y rows are deleted.')

		# Insert to X table
		obj = {'X': X}
		r.db(config['DB_NAME']).table('X').insert(obj).run(connection)
		print('Successfully inserted X to the', config['DB_NAME'], 'database.')

		# Insert to y table
		obj = {'y': y}
		r.db(config['DB_NAME']).table('y').insert(obj).run(connection)
		print('Successfully inserted y to the', config['DB_NAME'], 'database.')

		return num


	def get_word_indices(self, tokens):
		"""
		Returns the word indices from the token list
		"""
		word_indices = []

		temp_vocab_list = np.array(self.vocab_list)
		for token in tokens:
			word_indices.extend(np.where(temp_vocab_list == token)[0].tolist())

		return word_indices


	def get_feature_vector(self, word_indices):
		"""
		Returns a feature vector
		"""

		# Set the elements of the feature vector to 0
		feature_vector = np.zeros(self.n)

		for index in word_indices:
			feature_vector[index] = 1

		return feature_vector.tolist()


	def identify_class(self, tokens):
		"""
		Identifies the class of the review based on the total sentiment scores
		"""
		score = 0
		total_obj_score = 0
		total_available_synsets = 0
		n = 0

		for word in tokens:
			word_obj_score = 0
			synset_list = list(swn.senti_synsets(word))

			if (len(synset_list) > 0):
				total_available_synsets += 1
				for synset in synset_list:
					score += (synset.pos_score() - synset.neg_score())
					# word_obj_score += synset.obj_score()
					total_obj_score += synset.obj_score()
					n += 1

				# word_obj_score = word_obj_score / len(synset_list)
				# total_obj_score += word_obj_score

		# total_obj_score = total_obj_score / total_available_synsets
		if (n == 0):
			return 'no senti synsets'

		total_obj_score = total_obj_score / n
		small_delta = 0

		# This approach was used by Liu and Lee (2015)
		if (total_obj_score < small_delta):
			return -1
		elif (total_obj_score > small_delta):
			return 1
		else:
			return 0

		# The objectivity is the mean of each word's objectivity means
		# if (score > 0.2):
		# 	return 1
		# elif (score < -0.2):
		# 	return -1
		# else:
		# 	return 0

		# if (total_obj_score >= 0.875):
		# 	return 0
		# elif (score > 0):
		# 	return 1
		# else:
		# 	return -1


if __name__ == "__main__":
	feature_preprocessor = FeaturePreprocessor(500)
	num_of_english_reviews = feature_preprocessor.start(use_existing_vocab=True)
	print('Number of extracted English reviews:', num_of_english_reviews)

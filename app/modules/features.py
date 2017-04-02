import sys
import os
import time
import rethinkdb as r
import numpy as np

from rethinkdb.errors import RqlRuntimeError
from nltk.corpus import sentiwordnet as swn

from app.lib.rethinkdb_connect import connection
from app.modules.preprocessor import preprocess
from app.modules.vocabulary import create_vocabulary_list
# dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, dir_path + "/../lib")
# from rethinkdb_connect import connection
# sys.path.insert(0, dir_path + "/../modules")
# from preprocessor import preprocess
# from vocabulary import create_vocabulary_list


class FeaturePreprocessor:
	def __init__(self, vocab_size, model='unigram'):
		self.n = vocab_size
		self.vocab_list = []
		self.model = model
		self.start_time = None
		self.end_time = None


	def start(self):
		self.start_time = time.time()

		# Retrieve all the vocab data with the size specified
		cursor = r.table('vocab').filter({
			'size': self.n
		}).run(connection)

		for document in cursor:
			self.vocab_list = document['data']

		# Delete all the existing data on table
		r.table('X_' + self.model).delete().run(connection)
		r.table('y_' + self.model).delete().run(connection)

		num_of_reviews = r.table('combined_reviews').count().run(connection)
		cursor = r.table('combined_reviews').run(connection)

		num = total = 0
		for document in cursor:
			if self.model == 'unigram':
				num += self.unigram(document['data'], document['id'], document['label'], total, num_of_reviews)
				total += 1

			# Put bigram, trigram, and tfidf here

		print('Processed a total of', num, 'English reviews.')
		print('Total number of reviews (including non-English):', total)

		self.end_time = time.time()

		print('Total elapsed number of seconds: %s' % (self.end_time - self.start_time))

		return num


	def unigram(self, review, ID, label, total, num_of_reviews):
		"""
		Extracts the features of a review
		"""
		print(total, '----', total*100//num_of_reviews , '%', end='\r')
		tokens = preprocess(review)

		# If the language of the review is not English
		if tokens == -1:
			return 0

		word_indices = self.get_word_indices(tokens)
		feature_vector = self.get_feature_vector(word_indices)

		r.table('X_' + self.model).insert({
			'id': ID,
			'data': feature_vector
		}).run(connection)

		r.table('y_' + self.model).insert({
			'id': ID,
			'data': label
		}).run(connection)

		return 1


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
		feature_vector = np.zeros(self.n)

		for index in word_indices:
			feature_vector[index] = 1

		return feature_vector.tolist()


if __name__ == "__main__":
	feature_preprocessor = FeaturePreprocessor(10000, model='unigram')
	num_of_english_reviews = feature_preprocessor.start()

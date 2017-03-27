import sys
import os
import operator
import rethinkdb as r

from app.configuration.config import config
from app.modules.preprocessor import preprocess
from app.lib.rethinkdb_connect import connection


def create_vocabulary_list(reviews, vocab_size):
	"""
	Creates a list of the top VOCAB_SIZE words (sorted by their frequency in descending order)
	"""
	vocab_list = []
	tuple_list = get_vocabulary_list(reviews)

	print('Number of unique words:', len(tuple_list))
	for i in range(vocab_size):
		vocab_list.append(tuple_list[i][0])

	obj = {
		str(vocab_size): vocab_list,
		'size': vocab_size
	}

	# Delete all rows of vocab table
	r.db(config['DB_NAME']).table('vocab').filter({
		'size': vocab_size
	}).delete().run(connection)
	print('All vocab rows are deleted.')

	# Insert to vocab table
	r.db(config['DB_NAME']).table('vocab').insert(obj).run(connection)
	print('New vocab rows are inserted.')


def get_vocabulary_list(reviews):
	"""
	Retrieves the list of tuples of each word frequency
	"""
	freq_map = {}

	total = 0
	for review in reviews:
		tokens = preprocess(review)

		# If the language of the review is not English
		if (tokens == -1):
			continue

		total += 1
		print(total)
		for token in tokens:
			if token in freq_map:
				freq_map[token] += 1
			else:
				freq_map[token] = 1

	print('Number of English reviews:', total)

	# Sort the list of freq_map's tuples by their value
	sorted_freq_map = sorted(freq_map.items(), key=operator.itemgetter(1), reverse=True)

	return sorted_freq_map

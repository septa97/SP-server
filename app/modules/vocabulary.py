import sys
import os
import operator
import rethinkdb as r

from app.lib.rethinkdb_connect import connection
from app.modules.preprocessor import preprocess
# dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, dir_path + "/../lib")
# from rethinkdb_connect import connection
# sys.path.insert(0, dir_path + "/../modules")
# from preprocessor import preprocess


def create_vocabulary_list(reviews, vocab_size, model):
	"""
	Creates a list of the top VOCAB_SIZE words (sorted by their frequency in descending order)
	"""
	vocab_list = []
	tuple_list = get_vocabulary_list(reviews)

	print('Number of unique words:', len(tuple_list))
	for i in range(vocab_size):
		vocab_list.append(tuple_list[i][0])

	# Delete all rows of vocab table
	r.table('vocab').filter({
		'id': model
	}).delete().run(connection)
	print('All vocab rows are deleted.')

	obj = {
		'id': model,
		'size': vocab_size,
		'data': vocab_list
	}

	# Insert to vocab table
	r.table('vocab').insert(obj).run(connection)
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

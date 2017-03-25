import operator
from preprocessor import preprocess

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../configuration")
from config import config


def create_vocabulary_list(reviews):
	"""
	Creates a list of the top VOCAB_SIZE words (sorted by their frequency in descending order)
	"""
	vocab_list = []
	tuple_list = get_vocabulary_list(reviews)

	print('Number of unique words:', len(tuple_list))
	for i in range(config['VOCAB_SIZE']):
		vocab_list.append(tuple_list[i][0])

	return vocab_list


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
		for token in tokens:
			if token in freq_map:
				freq_map[token] += 1
			else:
				freq_map[token] = 1

	print('Number of English reviews:', total)

	# Sort the list of freq_map's tuples by their value
	sorted_freq_map = sorted(freq_map.items(), key=operator.itemgetter(1), reverse=True)

	return sorted_freq_map

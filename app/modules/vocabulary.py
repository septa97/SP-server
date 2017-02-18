import operator
from preprocessor import preprocess
from config import config

# Function that creates a list of the top VOCAB_SIZE words (sorted by their frequency in descending order)
# Input: a list of tuples
# Output: a list of string
def create_vocabulary_list(reviews):
	vocab_list = []
	tuple_list = get_vocabulary_list(reviews)

	print('Number of unique words:', len(tuple_list))
	for i in range(config['VOCAB_SIZE']):
		vocab_list.append(tuple_list[i][0])

	return vocab_list


# Function that retrieves the list of tuples of each word frequency
# Input: a list of unpreprocessed reviews
# Output: a list of tuples
def get_vocabulary_list(reviews):
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

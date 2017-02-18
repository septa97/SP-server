import rethinkdb as r
import numpy as np
import pandas as pd
from nltk.corpus import sentiwordnet as swn
from preprocessor import preprocess
from vocabulary import create_vocabulary_list
from config import config

# Globals
reviews = []
vocab_list = []
n = config['VOCAB_SIZE']

# Function that retrieves all the reviews and writes the vocabulary list to vocab.csv
# Input: N/A
# Output: N/A
def init():
	global reviews, vocab_list
	connection = r.connect(config['HOST'], config['PORT'])
	cursor = r.db(config['DB_NAME']).table('reviews').run(connection)
	rows = []

	for document in cursor:
		rows.append(document)

	for row in rows:
		slug = list(filter(lambda k: k != 'id', row.keys()))[0]
		reviews.extend(row[slug])

	# vocab_list = create_vocabulary_list(reviews)

	# Write to vocab.csv
	# df = pd.DataFrame(vocab_list, columns=['feature_words'])
	# df.to_csv('vocab.csv', index=False)

	extract_features_and_labels()


# Function that extracts the features of a list of reviews the writes to X.csv and y.csv
# Input: N/A
# Output: N/A
def extract_features_and_labels():
	vocab_list = pd.read_csv('vocab.csv')

	X = pd.DataFrame()
	y = pd.DataFrame()

	num = 0
	for review in reviews:
		tokens = preprocess(review)

		# If the language of the review is not English
		if (tokens == -1):
			continue

		word_indices = get_word_indices(tokens, vocab_list)
		num += 1
		print(num)
		feature_vector = get_feature_vector(word_indices)
		X = X.append(feature_vector.T)

		classification = identify_class(tokens)
		y = y.append([classification])

	# Write X and y to X.csv and y.csv respectively
	X.to_csv('X.csv', index=False)
	y.to_csv('y.csv', index=False)


# Function that returns a feature vector {0, 1}
# Input: list of word index
# Output: n x 1 DataFrame
def get_feature_vector(word_indices):
	# Set the elements of the feature vector to 0
	feature_vector = pd.DataFrame(0, index=np.arange(0, n), columns=np.arange(1))

	for index in word_indices:
		feature_vector.loc[index] = 1

	return feature_vector


# Function that returns the word indices from the list of token
# Input: list of tokens, list of vocabulary
# Output: a list of the word indices
def get_word_indices(tokens, vocab_list):
	word_indices = []

	for token in tokens:
		word_indices.extend(vocab_list[(vocab_list['feature_words'] == token)].index.tolist())

	return word_indices


# Function that identify the class of the review based on the total sentiment scores (this will serve as the actual value of the review)
# Input: a list of tokens of a review
# Output: a class which is an element of {1, -1, 0}
def identify_class(tokens):
	score = 0
	
	for word in tokens:
		synset_list = list(swn.senti_synsets(word))

		for synset in synset_list:
			score += (synset.pos_score() - synset.neg_score())

	if (score > 0):
		return 1
	elif (score < 0):
		return -1
	else:		# WILL CHANGE THIS LATER. OBJECTIVITY WILL BE MEASURED FOR NEUTRALITY INSTEAD
		return 0


init()

import nltk
import langdetect
import string

from nltk.corpus import sentiwordnet as swn
from langdetect.lang_detect_exception import LangDetectException

stopwords = nltk.corpus.stopwords.words('english')
langdetect.DetectorFactory.seed = 0
punctuation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
stemmer = nltk.stem.PorterStemmer()


def preprocess(review):
	"""
	Preprocess a review
	"""

	if not is_English(review):
		return -1

	# Convert to lowercase
	review = review.lower()

	# Remove punctuations
	review = review.translate(punctuation_table)

	tokens = nltk.word_tokenize(review)
	tokens = remove_stop_words(tokens)
	# tokens = stem_words(tokens)
	# pos_tags = nltk.pos_tag(tokens)

	return tokens


def is_English(review):
	"""
	Check if the language of a review is English
	"""
	try:
		language = langdetect.detect(review)
		if language != 'en':
			return False
	except LangDetectException:
		return False

	return True


def remove_stop_words(original_tokens):
	"""
	Remove the stop words from the review
	"""
	preprocessed_tokens = []

	# O(n^2)
	for token in original_tokens:
		if token not in stopwords:
			preprocessed_tokens.append(token)

	return preprocessed_tokens


def stem_words(original_tokens):
	"""
	Stem each token
	"""
	stemmed_tokens = []

	for token in original_tokens:
		stemmed_tokens.append(stemmer.stem(token))

	return stemmed_tokens

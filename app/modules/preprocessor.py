import nltk
import langdetect
import string
from nltk.corpus import sentiwordnet as swn
from langdetect.lang_detect_exception import LangDetectException

# Globals
stopwords = nltk.corpus.stopwords.words('english')
# langdetect.DetectorFactory.seed = 0
punctuation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))


# Function that preprocess a review
# Input: a single review (string)
# Output: a list of tokens
def preprocess(review):
	# Check if the language of the review is English and proceed if it is English
	try:
		language = langdetect.detect(review)
		if (language != 'en'):
			return -1
	except LangDetectException:
		return -1

	# Convert to lowercase
	review = review.lower()

	# Remove punctuations
	review = review.translate(punctuation_table)
	
	tokens = nltk.word_tokenize(review)
	tokens = remove_stop_words(tokens)
	# pos_tags = nltk.pos_tag(tokens)

	return tokens


# Function that removes the stop words from the review
# Input: a list of tokens that are not preprocessed
# Output: a list of preprocessed tokens
def remove_stop_words(original_tokens):
	preprocessed_tokens = []

	for token in original_tokens:
		if (token not in stopwords):
			preprocessed_tokens.append(token)

	return preprocessed_tokens

import sys
import os
import nltk
import numpy as np
import rethinkdb as r

from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, accuracy_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.svm import SVC

from app.lib.rethinkdb_connect import connection
from app.utils.rethinkdb_helpers import create_or_delete_table, insert_features
from app.utils.model_pickler import persist_to_disk

stopwords = nltk.corpus.stopwords.words('english')
dir_path = os.path.dirname(os.path.realpath(__file__))


def main(data_size, test_size=0.2, min_df=5, vocab_model='unigram', tf_idf=False, corrected=False):
	"""
	Perform Support Vector Classifier on the current data
	"""

	if corrected:
		reviews = load_files(dir_path + '/../data/reviews/corrected')
	else:
		reviews = load_files(dir_path + '/../data/reviews/not_corrected')

	if data_size != -1:
		text_train, text_test, y_train, y_test = train_test_split(reviews.data[:data_size], reviews.target[:data_size], test_size=test_size, random_state=0)
	else:
		text_train, text_test, y_train, y_test = train_test_split(reviews.data, reviews.target, test_size=test_size, random_state=0)

	if tf_idf:
		if vocab_model == 'unigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(1, 1))
			transformer = TfidfTransformer(use_idf=True)
		if vocab_model == 'bigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(2, 2))
			transformer = TfidfTransformer(use_idf=True)
		if vocab_model == 'trigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(3, 3))
			transformer = TfidfTransformer(use_idf=True)
	else:
		if vocab_model == 'unigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(1, 1))
			transformer = TfidfTransformer(use_idf=False)
		if vocab_model == 'bigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(2, 2))
			transformer = TfidfTransformer(use_idf=False)
		if vocab_model == 'trigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(3, 3))
			transformer = TfidfTransformer(use_idf=False)

	# PIPELINED WITH K-FOLD CROSS VALIDATION
	# Support Vector Classifier (one vs rest strategy, RBF/Gaussian kernel)
	# clf = SVC(decision_function_shape='ovr', kernel='rbf', verbose=False)

	# parameters = {
	# 	'clf__C': np.logspace(-4, 4, 10).tolist()
	# }

	# pipe = Pipeline([
	# 		('vect', vect),
	# 		('transformer', transformer),
	# 		('clf', clf)
	# 	])

	# grid_search = GridSearchCV(pipe, parameters, cv=10, n_jobs=-1, verbose=False)
	# grid_search.fit(text_train, y_train)

	# y_train_pred = grid_search.predict(text_train)
	# y_test_pred = grid_search.predict(text_test)

	# TRAIN-TEST SPLIT (80-20)
	clf = SVC(C=1000, decision_function_shape='ovr', kernel='rbf', probability=True, verbose=False)

	pipe = make_pipeline(vect, clf)
	pipe.fit(text_train, y_train)

	y_train_pred = pipe.predict(text_train)
	y_test_pred = pipe.predict(text_test)
	###################################################
	train_score = accuracy_score(y_train, y_train_pred)
	test_score = accuracy_score(y_test, y_test_pred)
	score_f1 = f1_score(y_train, y_train_pred, average='weighted')
	score_precision = precision_score(y_train, y_train_pred, average='weighted')
	score_recall = recall_score(y_train, y_train_pred, average='weighted')

	print('(sklearn) Train data accuracy:', train_score)
	print('(sklearn) Test data accuracy:', test_score)

	cm_train = confusion_matrix(y_train, y_train_pred)
	cm_test = confusion_matrix(y_test, y_test_pred)

	# Save the features to RethinkDB server
	create_or_delete_table('features')
	insert_features(vocab_model, tf_idf, vect.vocabulary_.keys())

	if data_size == -1:
		persist_to_disk('SVM', vocab_model, tf_idf, corrected, pipe, vect.vocabulary_)
		data_size = len(reviews.data)

	return train_score, test_score, len(text_train), len(text_test), cm_train, cm_test, score_f1, score_precision, score_recall, vect.vocabulary_, data_size


if __name__ == "__main__":
	main(-1)

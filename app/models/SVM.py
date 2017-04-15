import sys
import os
import nltk
import numpy as np
import rethinkdb as r

from sklearn.datasets import load_files
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, accuracy_score
from sklearn.svm import SVC

from app.lib.rethinkdb_connect import connection
from app.utils.rethinkdb_helpers import create_or_delete_table

dir_path = os.path.dirname(os.path.realpath(__file__))
stopwords = nltk.corpus.stopwords.words('english')


def main(data_size, test_size=0.2, min_df=5, vocab_model='unigram', tf_idf=False, corrected=False):
	"""
	Perform Support Vector Classifier on the current data
	"""

	if corrected:
		reviews = load_files(dir_path + '/../data/reviews/corrected')
	else:
		reviews = load_files(dir_path + '/../data/reviews/not_corrected')

	split = int(len(reviews.data) * (1 - test_size))

	if data_size != -1:
		text_train, text_test, y_train, y_test = train_test_split(reviews.data[:data_size], reviews.target[:data_size], test_size=test_size, random_state=0)
	else:
		text_train, text_test, y_train, y_test = train_test_split(reviews.data, reviews.target, test_size=test_size, random_state=0)

	if tf_idf:
		if vocab_model == 'unigram':
			vect = TfidfVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(1, 1)).fit(text_train)
		if vocab_model == 'bigram':
			vect = TfidfVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(2, 2)).fit(text_train)
		if vocab_model == 'trigram':
			vect = TfidfVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(3, 3)).fit(text_train)
	else:
		if vocab_model == 'unigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(1, 1)).fit(text_train)
		if vocab_model == 'bigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(2, 2)).fit(text_train)
		if vocab_model == 'trigram':
			vect = CountVectorizer(min_df=min_df, stop_words=stopwords, ngram_range=(3, 3)).fit(text_train)

	X_train = vect.transform(text_train)
	X_test = vect.transform(text_test)

	# Support Vector Classifier (one vs rest strategy, RBF/Gaussian kernel)
	clf = SVC(C=1000, decision_function_shape='ovr', kernel='rbf', verbose=True)
	clf.fit(X_train, y_train)

	y_train_pred = clf.predict(X_train)
	y_test_pred = clf.predict(X_test)
	train_score = accuracy_score(y_train, y_train_pred)
	test_score = accuracy_score(y_test, y_test_pred)
	score_f1 = f1_score(y_train, y_train_pred, average='weighted')
	score_precision = precision_score(y_train, y_train_pred, average='weighted')
	score_recall = recall_score(y_train, y_train_pred, average='weighted')

	print('(sklearn) Train data accuracy:', train_score)
	print('(sklearn) Test data accuracy:', test_score)

	cm_train = confusion_matrix(y_train, y_train_pred)
	cm_test = confusion_matrix(y_test, y_test_pred)

	# Persist the classifier and vocabulary
	create_or_delete_table('features')

	r.table('features').insert({
			'id': vocab_model,
			'tf_idf': tf_idf,
			'data': vect.vocabulary_.keys()
		}).run(connection)

	if tf_idf:
		joblib.dump(clf, '%s/../data/models/SVM_%s_tfidf.pkl' % (dir_path, vocab_model))
		joblib.dump(vect.vocabulary_, '%s/../data/vocabulary/%s_tfidf.pkl' % (dir_path, vocab_model))
	else:
		joblib.dump(clf, '%s/../data/models/SVM_%s.pkl' % (dir_path, vocab_model))
		joblib.dump(vect.vocabulary_, '%s/../data/vocabulary/%s.pkl' % (dir_path, vocab_model))

	if data_size == -1:
		data_size = len(reviews.data)

	return train_score, test_score, X_train.shape[0], X_test.shape[0], cm_train, cm_test, score_f1, score_precision, score_recall, vect.vocabulary_, data_size


if __name__ == "__main__":
	main()

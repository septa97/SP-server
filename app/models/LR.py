import sys
import os
import numpy as np
import rethinkdb as r

from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_files
from sklearn.metrics import confusion_matrix
from sklearn.feature_extraction.text import CountVectorizer

from app.lib.rethinkdb_connect import connection
from app.utils.data_manipulation import feature_scale, train_test_split
from app.utils.data_operation import accuracy_score
dir_path = os.path.dirname(os.path.realpath(__file__))


def main(test_size=0.2, min_df=5):
	"""
	Perform Logistic Regression on the current data
	"""

	reviews = load_files(dir_path + '/../data')

	split = int(len(reviews.data) * (1 - test_size))
	text_train, y_train = reviews.data[:split], reviews.target[:split]
	text_test, y_test = reviews.data[split:], reviews.target[split:]

	vect = CountVectorizer(min_df=min_df, stop_words="english").fit(text_train)
	X_train = vect.transform(text_train)
	X_test = vect.transform(text_test)

	# Logistic Regression (one vs rest strategy)
	clf = LogisticRegression(solver='newton-cg', multi_class='ovr', verbose=True)
	clf.fit(X_train, y_train)

	train_score = clf.score(X_train, y_train)
	test_score = clf.score(X_test, y_test)

	print('(sklearn) Train data accuracy:', train_score)
	print('(sklearn) Test data accuracy:', test_score)

	cm_train = confusion_matrix(y_train, clf.predict(X_train))
	cm_test = confusion_matrix(y_test, clf.predict(X_test))

	return train_score, test_score, X_train.shape[0], X_test.shape[0], cm_train, cm_test


if __name__ == "__main__":
	main()

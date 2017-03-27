import sys
import os
import numpy as np
import rethinkdb as r

from sklearn import neural_network
from sklearn.metrics import confusion_matrix

from app.configuration.config import config
from app.lib.rethinkdb_connect import connection
from app.utils.data_manipulation import feature_scale, train_test_split
from app.utils.data_operation import accuracy_score
from app.utils.data_plotting import plot_confusion_matrix


def main(test_size=0.2):
	# Load X and y
	X = np.array(r.db(config['DB_NAME']).table('X').nth(0).run(connection)['X'])
	y = np.array(r.db(config['DB_NAME']).table('y').nth(0).run(connection)['y'])

	# Split the data into training and testing set
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

	# Multi-layer Perceptron Classifier
	clf = neural_network.MLPClassifier(solver='adam', hidden_layer_sizes=(100,), random_state=1, verbose=True, activation='relu', max_iter=200)
	clf.fit(X_train, y_train)

	training_score = clf.score(X_train, y_train)
	test_score = clf.score(X_test, y_test)

	print('(sklearn) Training data accuracy:', training_score)
	print('(sklearn) Test data accuracy:', test_score)

	return training_score, test_score, X_train.shape[0]


if __name__ == "__main__":
	main()

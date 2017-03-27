import sys
import os
import numpy as np
import rethinkdb as r

from sklearn import svm
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
	X_train, X_test, y_train, y_test = train_test_split(X, y)

	# Support Vector Classifier (one vs rest strategy, RBF/Gaussian kernel)
	clf = svm.SVC(C=1, decision_function_shape='ovr', kernel='rbf', verbose=True)
	clf.fit(X_train, y_train)

	training_score = clf.score(X_train, y_train)
	test_score = clf.score(X_test, y_test)

	print('(sklearn) Training data accuracy:', training_score)
	print('(sklearn) Test data accuracy:', test_score)

	return training_score, test_score, X_train.shape[0]

	# Compute and plot the confusion matrix
	# plt.figure()
	# cnf_matrix = confusion_matrix(y_test, clf.predict(X_test))
	# plot_confusion_matrix(cnf_matrix, target_names, title='Confusion matrix, without normalization')
	# mpld3.show()


if __name__ == "__main__":
	main()

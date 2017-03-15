import sys
import os
import numpy as np
import pandas as pd
from sklearn import svm

# Import helper functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../utils")
from data_manipulation import feature_scale, train_test_split
from data_operation import accuracy_score

def main():
	X = np.loadtxt('X_temp.txt', delimiter=',')
	y = np.loadtxt('y_temp.txt', delimiter=',')

	X_train, X_test, y_train, y_test = train_test_split(X, y)

	clf = svm.SVC(C=1, decision_function_shape='ovr', kernel='rbf', verbose=True)
	clf.fit(X_train, y_train)

	training_score = clf.score(X_train, y_train)
	test_score = clf.score(X_test, y_test)

	print('(sklearn) Training data accuracy:', training_score)
	print('(sklearn) Test data accuracy:', test_score)

if __name__ == "__main__":
	main()

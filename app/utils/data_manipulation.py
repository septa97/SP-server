import numpy as np

def feature_scale(X):
	"""
	Scales the feature values based on the minimum and maximum values
	"""
	row, col = X.shape

	for j in range(0, col):
		maximum = np.max(X[:, j])
		minimum = np.min(X[:, j])

		X[:, j] = (X[:, j] - minimum) / (maximum - minimum)

	return X

def train_test_split(X, y, test_size=0.2, shuffle=False):
	"""
	Split the data into training and testing set
	"""
	m, n = X.shape

	split = int(m * (1 - test_size))
	X_train, X_test = X[:split], X[split:]
	y_train, y_test = y[:split], y[split:]

	return X_train, X_test, y_train, y_test

def add_bias_weights(X):
	"""
	Add the bias weights to the data
	"""
	X = np.insert(X, 0, 1, axis=1)

	return X

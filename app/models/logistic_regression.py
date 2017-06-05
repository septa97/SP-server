import sys
import os
import nltk
import numpy as np

from scipy.optimize import minimize
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

stopwords = nltk.corpus.stopwords.words('english')
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/../utils')

from data_manipulation import add_bias_weights


# The sigmoid function
def sigmoid(x):
	return 1 / (1 + np.exp(-x))

# Safe ln
def safe_ln(x, minval=0.0000000001):
	return np.log(x.clip(min=minval))

class LogisticRegression:
	def __init__(self, l=1, threshold=0.5):
		self.l = l
		self.threshold = threshold
		self.iterations = 0
		self.m = None
		self.n = None
		self.theta = None
		self.curr_X = None
		self.curr_y = None

	def iteration_callback(self, theta):
		self.theta = theta
		self.iterations += 1
		cost, grad = self.compute_cost_and_grad(self.theta, self.curr_X, self.curr_y)
		print('Iteration', self.iterations, ', Current cost:', cost)

	def compute_cost_and_grad(self, theta, X, y):
		"""
		Computes the cost and gradient of the function
		"""
		grad = np.zeros(self.n)

		# Predicted values using the current theta
		h = sigmoid(X.dot(theta))

		# Vectorized implementation
		J = -1/self.m * (y.dot(safe_ln(h)) + (1-y).dot(safe_ln(1-h))) + (self.l/(2*self.m) * theta[1:].dot(theta[1:]))

		# Regularized gradient computation
		grad[0] = 1/self.m * X[:, 0].T.dot(h - y)
		grad[1:] = (1/self.m * X[:, 1:].T.dot(h - y)) + (self.l/self.m * theta[1:])

		return J, grad

	def fit(self, X, y, maxiter=100):
		X = add_bias_weights(X)
		self.curr_X = X
		self.curr_y = y
		self.m, self.n = X.shape
		self.theta = np.zeros(self.n)

		cost, grad = self.compute_cost_and_grad(self.theta, self.curr_X, self.curr_y)
		print('(Initial theta) Iteration', self.iterations, ', Current cost:', cost)
		minimize(self.compute_cost_and_grad, self.theta, method='BFGS', jac=True, args=(X, y), callback=self.iteration_callback, options={'disp': True, 'maxiter': maxiter})

	def predict(self, X):
		X = add_bias_weights(X)
		m = X.shape[0]
		p = np.zeros(m)
		h = sigmoid(X.dot(self.theta))

		for i in range(0, m):
			if h[i] >= self.threshold:
				p[i] = 1

		return p


def main():
	reviews = load_files(dir_path + '/../data/reviews/not_corrected')
	text_train, text_test, y_train, y_test = train_test_split(reviews.data, reviews.target, test_size=0.2, random_state=0)

	vect = CountVectorizer(min_df=5, stop_words=stopwords, ngram_range=(1, 1))
	X_train = vect.fit_transform(text_train)
	X_test = vect.transform(text_test)

	# clf = LogisticRegression()
	# clf.fit(X_train, y_train)
	# y_test_pred = clf.predict(X_test)

	# print(accuracy_score(y_test, y_test_pred))

if __name__ == "__main__":
	main()

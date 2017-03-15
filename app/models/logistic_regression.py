import sys
import os
import numpy as np
from scipy.optimize import minimize

# Import helper functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../utils")
from data_manipulation import feature_scale, train_test_split, add_bias_weights
from data_operation import accuracy_score


# The sigmoid function
def sigmoid(x):
	return 1 / (1 + np.exp(-x))

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

		# total = 0
		# for i in range(0, self.m):
		# 	if (y[i] == 1):
		# 		total = total + np.log(h[i])
		# 	else:
		# 		total = total + np.log(1 - h[i])

		# # Regularized cost function
		# J = -1/self.m * total + (self.l/(2*self.m) * theta[1:].dot(theta[1:]))

		# Vectorized implementation
		J = -1/self.m * (y.dot(np.log(h)) + (1-y).dot(np.log(1-h))) + (self.l/(2*self.m) * theta[1:].dot(theta[1:]))

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
			if (h[i] >= self.threshold):
				p[i] = 1

		return p


def main():
	X = np.loadtxt('X_temp.txt', delimiter=',')
	y = np.loadtxt('y_temp.txt', delimiter=',')

	X_train, X_test, y_train, y_test = train_test_split(X, y)

	clf = LogisticRegression()
	clf.fit(X_train, y_train, maxiter=400)

	train_predicted = clf.predict(X_train)
	test_predicted = clf.predict(X_test)

	train_accuracy = accuracy_score(y_train, train_predicted)
	test_accuracy = accuracy_score(y_test, test_predicted)

	print('Train Accuracy:', train_accuracy)
	print('Test Accuracy:', test_accuracy)


if __name__ == "__main__":
	main()

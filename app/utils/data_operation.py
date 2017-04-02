import numpy as np


def accuracy_score(actual, predicted):
	"""
	Computes the accuracy
	"""
	m = actual.size
	correct = 0

	for i in range(0, m):
		if actual[i] == predicted[i]:
			correct += 1

	return correct / m

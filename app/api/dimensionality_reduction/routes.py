import sys
import os
import numpy as np
import rethinkdb as r

from flask import Blueprint, jsonify, request
from sklearn.decomposition import PCA, KernelPCA, SparsePCA
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE

from app.configuration.config import config
from app.lib.rethinkdb_connect import connection

dir_path = os.path.dirname(os.path.realpath(__file__))


mod = Blueprint('dimensionality-reduction', __name__)

@mod.route('/PCA/<int:min_df>/<int:rows>/<int:n_components>', methods=['GET'])
def principal_component_analysis(min_df, rows, n_components):
	"""
	Returns the PCA dimension-reduced data with n_components as the number of the new dimensions
	"""
	data = {
		'positive': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'negative': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'neutral': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		}
	}

	# Load the vocab size
	reviews = load_files(dir_path + '/../../data')
	text, y = reviews.data[:rows], reviews.target[:rows]
	classes = {k: v for k, v in zip(np.unique(y), reviews.target_names)}

	for i in range(0, len(text)):
		data[classes[y[i]]]['reviews'].append(text[i].decode('utf-8'))

	vect = CountVectorizer(min_df=min_df, stop_words="english").fit(text)
	X = vect.transform(text)

	# Principal Component Analysis
	pca = PCA(n_components=n_components)
	X_reduced = pca.fit_transform(X.toarray())

	for i, c in zip(np.unique(y), reviews.target_names):
		data[c]['X'] = X_reduced[y == i, 0].tolist()
		data[c]['y'] = X_reduced[y == i, 1].tolist()

		if n_components == 3:
			data[c]['z'] = X_reduced[y == i, 2].tolist()

	return jsonify(data)


@mod.route('/tSNE/<int:min_df>/<int:rows>/<int:n_components>', methods=['GET'])
def t_distributed_stochastic_neighbor_embedding(min_df, rows, n_components):
	"""
	Returns the tSNE dimension-reduced data with n_components as the number of the new dimensions
	"""
	data = {
		'positive': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'negative': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'neutral': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		}
	}

	# Load the vocab size
	reviews = load_files(dir_path + '/../../data')
	text, y = reviews.data[:rows], reviews.target[:rows]
	classes = {k: v for k, v in zip(np.unique(y), reviews.target_names)}

	for i in range(0, len(text)):
		data[classes[y[i]]]['reviews'].append(text[i].decode('utf-8'))

	vect = CountVectorizer(min_df=min_df, stop_words="english").fit(text)
	X = vect.transform(text)

	# Principal Component Analysis
	tsne = TSNE(n_components=n_components, init='pca', random_state=0)
	X_reduced = tsne.fit_transform(X.toarray())

	for i, c in zip(np.unique(y), reviews.target_names):
		data[c]['X'] = X_reduced[y == i, 0].tolist()
		data[c]['y'] = X_reduced[y == i, 1].tolist()

		if n_components == 3:
			data[c]['z'] = X_reduced[y == i, 2].tolist()

	return jsonify(data)

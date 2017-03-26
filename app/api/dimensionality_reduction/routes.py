import sys
import os
import numpy as np
import rethinkdb as r

from flask import Blueprint, jsonify, request
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from app.configuration.config import config
from app.lib.rethinkdb_connect import connection


mod = Blueprint('dimensionality-reduction', __name__)

@mod.route('/PCA/<int:n_components>', methods=['GET'])
def principal_component_analysis(n_components):
	"""
	Returns the PCA dimension-reduced data with n_components as the number of the new dimensions
	"""
	data = {
		'positive': {
			'X': [],
			'y': [],
			'z': []
		},
		'negative': {
			'X': [],
			'y': [],
			'z': []
		},
		'neutral': {
			'X': [],
			'y': [],
			'z': []
		}
	}

	# Load X and y
	X = np.array(r.db(config['DB_NAME']).table('X').nth(0).run(connection)['X'])
	y = np.array(r.db(config['DB_NAME']).table('y').nth(0).run(connection)['y'])

	# Principal Component Analysis
	pca = PCA(n_components=n_components)
	X_reduced = pca.fit_transform(X)

	for i, c in zip([-1, 0, 1], ['negative', 'neutral', 'positive']):
		data[c]['X'] = X_reduced[y == i, 0].tolist()
		data[c]['y'] = X_reduced[y == i, 1].tolist()

		if (n_components == 3):
			data[c]['z'] = X_reduced[y == i, 2].tolist()

	return jsonify(data)


@mod.route('/tSNE/<int:n_components>', methods=['GET'])
def t_distributed_stochastic_neighbor_embedding(n_components):
	"""
	Returns the tSNE dimension-reduced data with n_components as the number of the new dimensions
	"""
	data = {
		'positive': {
			'X': [],
			'y': [],
			'z': []
		},
		'negative': {
			'X': [],
			'y': [],
			'z': []
		},
		'neutral': {
			'X': [],
			'y': [],
			'z': []
		}
	}

	# Load X and y
	X = np.array(r.db(config['DB_NAME']).table('X').nth(0).run(connection)['X'])
	y = np.array(r.db(config['DB_NAME']).table('y').nth(0).run(connection)['y'])

	# Principal Component Analysis
	tsne = TSNE(n_components=n_components, init='pca', random_state=0)
	X_reduced = tsne.fit_transform(X)

	for i, c in zip([-1, 0, 1], ['negative', 'neutral', 'positive']):
		data[c]['X'] = X_reduced[y == i, 0].tolist()
		data[c]['y'] = X_reduced[y == i, 1].tolist()

		if (n_components == 3):
			data[c]['z'] = X_reduced[y == i, 2].tolist()

	return jsonify(data)

import logging
import sys
import os
import gensim
import numpy as np
import rethinkdb as r

from flask import Blueprint, jsonify, request
from sklearn.decomposition import PCA, KernelPCA, SparsePCA
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.manifold import TSNE

from app.configuration.config import config
from app.lib.rethinkdb_connect import connection
from app.modules.preprocessor import preprocess

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


mod = Blueprint('dimensionality-reduction', __name__)

@mod.route('/PCA/<int:min_df>/<int:rows>/<int:n_components>', methods=['GET'])
def principal_component_analysis(min_df, rows, n_components):
	"""
	Returns the PCA dimension-reduced data with n_components as the number of the new dimensions
	"""
	data = {
		'very_positive': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'positive': {
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
		},
		'negative': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'very_negative': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		}
	}

	# The actual label will be used as class labels
	reviews = load_files(dir_path + '/../../data/reviews/not_corrected')
	text, y = reviews.data[:rows], reviews.target[:rows]
	classes = {k: v for k, v in zip(np.unique(y), reviews.target_names)}

	for i in range(0, len(text)):
		data[classes[y[i]]]['reviews'].append(text[i].decode('utf-8'))

	X = CountVectorizer(min_df=min_df, stop_words="english").fit_transform(text)

	# Principal Component Analysis
	X_reduced = KernelPCA(n_components=n_components, kernel='rbf', fit_inverse_transform=False).fit_transform(X.toarray())

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
		'very_positive': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'positive': {
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
		},
		'negative': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		},
		'very_negative': {
			'X': [],
			'y': [],
			'z': [],
			'reviews': []
		}
	}

	# The actual label will be used as class labels
	reviews = load_files(dir_path + '/../../data/reviews/not_corrected')
	text, y = reviews.data[:rows], reviews.target[:rows]
	classes = {k: v for k, v in zip(np.unique(y), reviews.target_names)}

	for i in range(0, len(text)):
		data[classes[y[i]]]['reviews'].append(text[i].decode('utf-8'))

	X = CountVectorizer(min_df=min_df, stop_words="english").fit_transform(text)

	# Principal Component Analysis
	X_reduced = TSNE(n_components=n_components, init='pca', random_state=0).fit_transform(X.toarray())

	for i, c in zip(np.unique(y), reviews.target_names):
		data[c]['X'] = X_reduced[y == i, 0].tolist()
		data[c]['y'] = X_reduced[y == i, 1].tolist()

		if n_components == 3:
			data[c]['z'] = X_reduced[y == i, 2].tolist()

	return jsonify(data)


@mod.route('/word2vec/<int:min_count>/<int:rows>/<int:n_components>', methods=['GET'])
def word2vec_word_embedding(min_count, rows, n_components):
	"""
	Returns the t-SNE dimension-reduced data of word embeddings with n_components
	as the new number of dimensions
	"""
	data = {
		'X': [],
		'y': [],
		'z': [],
		'words': []
	}

	# The actual label will be used as class labels
	reviews = load_files(dir_path + '/../../data/reviews/not_corrected').data

	preprocessed_reviews = [preprocess(review.decode('utf-8')) for review in reviews]
	model = gensim.models.Word2Vec(preprocessed_reviews, min_count=min_count, size=400)

	X = []

	for word in model.wv.index2word:
		X.append(model.wv[word])

	X = np.array(X)

	X_reduced = TSNE(n_components=n_components, init='pca', random_state=0).fit_transform(X)

	data['X'] = X_reduced[:rows, 0].tolist()
	data['y'] = X_reduced[:rows, 1].tolist()
	data['words'] = model.wv.index2word

	if n_components == 3:
		data['z'] = X_reduced[:rows, 2].tolist()

	return jsonify(data)

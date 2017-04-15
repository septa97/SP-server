import sys
import os
import nltk
import numpy as np
import rethinkdb as r

from flask import Blueprint, jsonify, request
from sklearn.datasets import load_files
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

from app.models.LR import main as LogisticRegression
from app.models.SVM import main as SupportVectorMachine
from app.models.MLP import main as MultiLayerPerceptron
from app.lib.rethinkdb_connect import connection
from app.utils.db_manipulation import save_to_performance

dir_path = os.path.dirname(os.path.realpath(__file__))
stopwords = nltk.corpus.stopwords.words('english')


mod = Blueprint('classifier', __name__)

@mod.route('/train', methods=['POST'])
def train():
	"""
	Train the classifier <classifier> based on the specified <testDataSize> and <minDF>. Return the performance scores afterwards.
	"""
	data = request.get_json(force=True)

	if data['classifier'] == 'LR':
		train_score, test_score, \
		train_size, test_size, \
		cm_train, cm_test, \
		f1_score, precision_score, \
		recall_score, vocabulary, \
		data_size = LogisticRegression(data_size=data['dataSize'],
			min_df=data['minDF'], vocab_model=data['vocabModel'],
			tf_idf=data['tfIdf'], corrected=data['corrected'])
	elif data['classifier'] == 'SVM':
		train_score, test_score, \
		train_size, test_size, \
		cm_train, cm_test, \
		f1_score, precision_score, \
		recall_score, vocabulary, \
		data_size = SupportVectorMachine(data_size=data['dataSize'],
			min_df=data['minDF'], vocab_model=data['vocabModel'],
			tf_idf=data['tfIdf'], corrected=data['corrected'])
	elif data['classifier'] == 'MLP':
		train_score, test_score, \
		train_size, test_size, \
		cm_train, cm_test, \
		f1_score, precision_score, \
		recall_score, vocabulary, \
		data_size = MultiLayerPerceptron(data_size=data['dataSize'],
			min_df=data['minDF'], vocab_model=data['vocabModel'],
			tf_idf=data['tfIdf'], corrected=data['corrected'])

	# Helper function for saving informations to the <performance> table
	save_to_performance(data_size, train_score, test_score, train_size,
		test_size, cm_train, cm_test, f1_score, precision_score, recall_score,
		data['classifier'], data['vocabModel'], data['tfIdf'], data['corrected'])

	data = []

	vocab_models = ['unigram', 'bigram', 'trigram']
	tf_idfs = [True, False]
	corrected = [True, False]

	for v in vocab_models:
		for t in tf_idfs:
			for c in corrected:
				obj = {
					'LR': [],
					'SVM': [],
					'MLP': [],
					'vocab_model': v,
					'tf_idf': t,
					'corrected': c
				}

				cursor = r.table('performance').filter({
						'vocab_model': v,
						'tf_idf': t,
						'corrected': c
					}).run(connection)

				for document in cursor:
					obj[document['classifier']].append({
							'data_size': document['data_size'],
							'train_size': document['train_size'],
							'train_score': document['train_score'],
							'test_size': document['test_size'],
							'test_score': document['test_score'],
							'cm_train': document['cm_train'],
							'cm_test': document['cm_test'],
							'f1_score': document['f1_score'],
							'precision_score': document['precision_score'],
							'recall_score': document['recall_score']
						})

				data.append(obj)

	return jsonify(data)


@mod.route('/existing-informations', methods=['GET'])
def get_existing_informations():
	"""
	Retrieves all the existing performance scores.
	"""
	data = []

	vocab_models = ['unigram', 'bigram', 'trigram']
	tf_idfs = [True, False]
	corrected = [True, False]

	for v in vocab_models:
		for t in tf_idfs:
			for c in corrected:
				obj = {
					'LR': [],
					'SVM': [],
					'MLP': [],
					'vocab_model': v,
					'tf_idf': t,
					'corrected': c
				}

				cursor = r.table('performance').filter({
						'vocab_model': v,
						'tf_idf': t,
						'corrected': c
					}).run(connection)

				for document in cursor:
					obj[document['classifier']].append({
							'data_size': document['data_size'],
							'train_size': document['train_size'],
							'train_score': document['train_score'],
							'test_size': document['test_size'],
							'test_score': document['test_score'],
							'cm_train': document['cm_train'],
							'cm_test': document['cm_test'],
							'f1_score': document['f1_score'],
							'precision_score': document['precision_score'],
							'recall_score': document['recall_score']
						})

				data.append(obj)

	return jsonify(data)


@mod.route('/classify/reviews', methods=['POST'])
def classify_reviews():
	"""
	Classify all the reviews
	"""
	data = request.get_json(force=True)

	if data['tfIdf']:
		clf = joblib.load('%s/../../data/models/%s_%s_tfidf.pkl' % (dir_path, data['classifier'], data['vocabModel']))
		vocabulary = joblib.load('%s/../../data/vocabulary/%s_tfidf.pkl' % (dir_path, data['vocabModel']))
	else:
		clf = joblib.load('%s/../../data/models/%s_%s.pkl' % (dir_path, data['classifier'], data['vocabModel']))
		vocabulary = joblib.load('%s/../../data/vocabulary/%s.pkl' % (dir_path, data['vocabModel']))

	vect = CountVectorizer(vocabulary=vocabulary)
	X = vect.transform(data['reviews'])
	y = np.array(data['ratings'])

	y_pred = clf.predict(X)
	accuracy = accuracy_score(y, y_pred)

	print('Accuracy:', accuracy * 100)

	return jsonify({
		'accuracy': accuracy,
		'predicted_label': y_pred.tolist()
	})

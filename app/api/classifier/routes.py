import sys
import os
import nltk
import numpy as np
import rethinkdb as r

from eli5.formatters import html, text, as_dict
from eli5.sklearn import explain_prediction, explain_weights, unhashing
from flask import Blueprint, jsonify, request
from sklearn.datasets import load_files
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegressionCV, LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

from app.models.LR import main as LR
from app.models.SVM import main as SVM
from app.models.MLP import main as MLP
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
		data_size = LR(data_size=data['dataSize'],
			min_df=data['minDF'], vocab_model=data['vocabModel'],
			tf_idf=data['tfIdf'], corrected=data['corrected'])
	elif data['classifier'] == 'SVM':
		train_score, test_score, \
		train_size, test_size, \
		cm_train, cm_test, \
		f1_score, precision_score, \
		recall_score, vocabulary, \
		data_size = SVM(data_size=data['dataSize'],
			min_df=data['minDF'], vocab_model=data['vocabModel'],
			tf_idf=data['tfIdf'], corrected=data['corrected'])
	elif data['classifier'] == 'MLP':
		train_score, test_score, \
		train_size, test_size, \
		cm_train, cm_test, \
		f1_score, precision_score, \
		recall_score, vocabulary, \
		data_size = MLP(data_size=data['dataSize'],
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
	test_size = 0.2
	min_df = 5

	reviews = load_files(dir_path + '/../../data/reviews/not_corrected')

	text_train, text_test, y_train, y_test = train_test_split(reviews.data, reviews.target, test_size=test_size, random_state=0)

	# if data['tfIdf']:
	# 	clf = joblib.load('%s/../../data/models/%s_%s_tfidf.pkl' % (dir_path, data['classifier'], data['vocabModel']))
	# 	vocabulary = joblib.load('%s/../../data/vocabulary/%s_tfidf.pkl' % (dir_path, data['vocabModel']))
	# else:
	# 	clf = joblib.load('%s/../../data/models/%s_%s.pkl' % (dir_path, data['classifier'], data['vocabModel']))
	# 	vocabulary = joblib.load('%s/../../data/vocabulary/%s.pkl' % (dir_path, data['vocabModel']))

	vect = TfidfVectorizer(min_df=min_df, stop_words="english", ngram_range=(1, 1)).fit(text_train)
	X_train = vect.transform(text_train)

	clf = LogisticRegression(solver='newton-cg', verbose=True)
	clf.fit(X_train, y_train)

	X = vect.transform(data['reviews'])
	y = np.array(data['ratings'])

	y_pred = clf.predict(X)
	accuracy = accuracy_score(y, y_pred)

	print('Accuracy:', accuracy * 100)

	return jsonify({
		'accuracy': accuracy,
		'predicted_label': y_pred.tolist()
	})


@mod.route('/explain/prediction', methods=['POST'])
def explain_review_prediction():
	"""Explain a specific prediction using the eli5 library
	"""
	data = request.get_json(force=True)
	test_size = 0.2
	min_df = 5

	reviews = load_files(dir_path + '/../../data/reviews/not_corrected')

	text_train, text_test, y_train, y_test = train_test_split(reviews.data, reviews.target, test_size=test_size, random_state=0)

	vect = TfidfVectorizer(min_df=min_df, stop_words='english', ngram_range=(1, 1)).fit(text_train)
	X_train = vect.transform(text_train)

	clf = LogisticRegression(solver='newton-cg', verbose=True)
	clf.fit(X_train, y_train)

	explanation = explain_prediction.explain_prediction_linear_classifier(clf, data['review'], vec=vect, target_names=reviews.target_names)
	div = html.format_as_html(explanation, include_styles=False)
	style = html.format_html_styles()

	return jsonify({
			'div': div,
			'style': style
		})


@mod.route('/explain/weights', methods=['GET'])
def explain_model_weights():
	"""Explain the weights/parameters of a certain model
	"""
	test_size = 0.2
	min_df = 5

	reviews = load_files(dir_path + '/../../data/reviews/not_corrected')

	text_train, text_test, y_train, y_test = train_test_split(reviews.data, reviews.target, test_size=test_size, random_state=0)

	vect = TfidfVectorizer(min_df=min_df, stop_words='english', ngram_range=(1, 1)).fit(text_train)
	X_train = vect.transform(text_train)

	clf = LogisticRegression(solver='newton-cg', verbose=True)
	clf.fit(X_train, y_train)

	explanation = explain_weights.explain_linear_classifier_weights(clf, vec=vect, target_names=reviews.target_names)
	div = html.format_as_html(explanation, include_styles=False)
	style = html.format_html_styles()

	return jsonify({
			'div': div,
			'style': style
		})

import sys
import os
import rethinkdb as r

from flask import Blueprint, jsonify, request

from app.models.LR import main as LogisticRegression
from app.models.SVM import main as SupportVectorMachine
from app.models.MLP import main as MultiLayerPerceptron
from app.lib.rethinkdb_connect import connection
from app.utils.db_manipulation import save_to_performance


mod = Blueprint('classifier', __name__)

@mod.route('/train', methods=['POST'])
def train():
	data = request.get_json(force=True)

	if data['classifier'] == 'LR':
		train_score, test_score, train_size, test_size, cm_train, cm_test = LogisticRegression(test_size=data['testDataSize'], min_df=data['minDF'])
		save_to_performance(train_score, test_score, train_size, test_size, cm_train, cm_test, data['classifier'])
	elif data['classifier'] == 'SVM':
		train_score, test_score, train_size, test_size, cm_train, cm_test = SupportVectorMachine(test_size=data['testDataSize'], min_df=data['minDF'])
		save_to_performance(train_score, test_score, train_size, test_size, cm_train, cm_test, data['classifier'])
	elif data['classifier'] == 'MLP':
		train_score, test_score, train_size, test_size, cm_train, cm_test = MultiLayerPerceptron(test_size=data['testDataSize'], min_df=data['minDF'])
		save_to_performance(train_score, test_score, train_size, test_size, cm_train, cm_test, data['classifier'])

	data = {}

	cursor = r.table('performance').run(connection)
	for document in cursor:
		data[document['classifier']] = {
			'train_size': document['train_size'],
			'train_score': document['train_score'],
			'test_size': document['test_size'],
			'test_score': document['test_score'],
			'cm_train': document['cm_train'],
			'cm_test': document['cm_test']
		}

	return jsonify(data)


@mod.route('/existing-informations', methods=['GET'])
def get_existing_informations():
	data = {
		'LR': [],
		'SVM': [],
		'MLP': []
	}

	cursor = r.table('performance').run(connection)

	for document in cursor:
		data[document['classifier']].append({
				'train_size': document['train_size'],
				'train_score': document['train_score'],
				'test_size': document['test_size'],
				'test_score': document['test_score'],
				'cm_train': document['cm_train'],
				'cm_test': document['cm_test']
			})

	return jsonify(data)

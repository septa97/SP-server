import rethinkdb as r

from flask import Blueprint, jsonify, request
from app.configuration.config import config
from app.lib.rethinkdb_connect import connection


mod = Blueprint('visualizer', __name__)

@mod.route('/LR-visualization-info', methods=['GET'])
def get_LR_visualization_info():
	cursor = r.db(config['DB_NAME']).table('LR').run(connection)
	data = {'informations': []}

	for document in cursor:
		data['informations'].append(document)

	return jsonify(data)


@mod.route('/SVM-visualization-info', methods=['GET'])
def get_SVM_visualization_info():
	cursor = r.db(config['DB_NAME']).table('SVM').run(connection)
	data = {'informations': []}

	for document in cursor:
		data['informations'].append(document)

	return jsonify(data)


@mod.route('/MLP-visualization-info', methods=['GET'])
def get_MLP_visualization_info():
	cursor = r.db(config['DB_NAME']).table('MLP').run(connection)
	data = {'informations': []}

	for document in cursor:
		data['informations'].append(document)

	return jsonify(data)

import rethinkdb as r

from flask import Blueprint, jsonify, request
from app.configuration.config import config
from app.lib.rethinkdb_connect import connection


mod = Blueprint('visualizer', __name__)

@mod.route('/visualization-info/<classifier>', methods=['GET'])
def get_LR_visualization_info(classifier):
	cursor = r.db(config['DB_NAME']).table(classifier).run(connection)
	data = {'informations': []}

	for document in cursor:
		data['informations'].append(document)

	return jsonify(data)

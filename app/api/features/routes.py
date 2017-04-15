import rethinkdb as r

from flask import Blueprint, jsonify, request

from app.lib.rethinkdb_connect import connection


mod = Blueprint('features', __name__)

@mod.route('/all', methods=['GET'])
def get_all_vocab():
	"""
	Retrieves all the vocabularies (unigram, bigram, and trigram).
	"""
	data = []

	cursor = r.table('features').run(connection)

	for document in cursor:
		data.append(document)

	return jsonify(data)

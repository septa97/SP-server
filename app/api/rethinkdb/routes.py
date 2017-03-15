import rethinkdb as r
from flask import Blueprint, jsonify
from app.modules.config import config
from app.lib.rethinkdb import connection

DB_NAME = config['DB_NAME']
mod = Blueprint('rethinkdb', __name__)

@mod.route('/reviews', methods=['GET'])
def get_all_reviews():
	cursor = r.db(DB_NAME).table('reviews').run(connection)
	reviews = []
	rows = []

	for document in cursor:
		rows.append(document)

	for row in rows:
		slug = list(filter(lambda k: k != 'id', row.keys()))[0]
		reviews.extend(row[slug])

	return jsonify(reviews)

import sys
import os
import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError

# from app.lib.rethinkdb_connect import connection

connection = r.connect('localhost', 28015, db='backup')


def create_or_delete_table(table, delete=False):
	try:
		r.table_create(table).run(connection)
		print('Successfully created table <%s>.' % table)
	except RqlRuntimeError:
		if delete:
			r.table(table).delete().run(connection)
			print('Table <%s> already exists. Deleted all existing documents instead.' % table)
		else:
			print('Table <%s> already exists.' % table)


def insert_features(vocab_model, tf_idf, data):
	cursor = r.table('features').filter({
			'vocab_model': vocab_model,
			'tf_idf': tf_idf
		}).run(connection)

	i = 0
	for document in cursor:
		i += 1

	if i == 0:
		r.table('features').insert({
				'vocab_model': vocab_model,
				'tf_idf': tf_idf,
				'data': data
			}).run(connection)

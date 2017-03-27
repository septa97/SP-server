import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError

from app.lib.rethinkdb_connect import connection
from app.configuration.config import config


def save_to_accuracy(training_score, test_score, training_size, classifier):
	"""
	Save all the important information (after training and testing) to the table accuracy
	"""
	try:
		r.db(config['DB_NAME']).table_create('accuracy').run(connection)
		print('Table accuracy successfully created.')
	except RqlRuntimeError:
		print('Table accuracy already exists.')

	r.db(config['DB_NAME']).table('accuracy').insert({
			'classifier': classifier,
			'training_score': training_score,
			'test_score': test_score,
			'training_size': training_size
		}).run(connection)

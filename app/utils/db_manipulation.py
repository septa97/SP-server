import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError

from app.lib.rethinkdb_connect import connection
from app.configuration.config import config


def save_to_LR(script, div, training_score, test_score, training_size):
	"""
	Save all the important information (after training and testing) to the table LR
	"""
	try:
		r.db(config['DB_NAME']).table_create('LR').run(connection)
		print('Table LR successfully created.')
	except RqlRuntimeError:
		print('Table LR already exists.')

	r.db(config['DB_NAME']).table('LR').insert({
			'script': script,
			'div': div,
			'training_score': training_score,
			'test_score': test_score,
			'training_size': training_size
		}).run(connection)


def save_to_SVM(script, div, training_score, test_score, training_size):
	"""
	Save all the important information (after training and testing) to the table SVM
	"""
	try:
		r.db(config['DB_NAME']).table_create('SVM').run(connection)
		print('Table SVM successfully created.')
	except RqlRuntimeError:
		print('Table SVM already exists.')

	r.db(config['DB_NAME']).table('SVM').insert({
			'script': script,
			'div': div,
			'training_score': training_score,
			'test_score': test_score,
			'training_size': training_size
		}).run(connection)


def save_to_MLP(script, div, training_score, test_score, training_size):
	"""
	Save all the important information (after training and testing) to the table MLP
	"""
	try:
		r.db(config['DB_NAME']).table_create('MLP').run(connection)
		print('Table MLP successfully created.')
	except RqlRuntimeError:
		print('Table MLP already exists.')

	r.db(config['DB_NAME']).table('MLP').insert({
			'script': script,
			'div': div,
			'training_score': training_score,
			'test_score': test_score,
			'training_size': training_size
		}).run(connection)

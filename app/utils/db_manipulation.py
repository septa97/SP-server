import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError

from app.lib.rethinkdb_connect import connection
from app.utils.rethinkdb_helpers import create_or_delete_table


def save_to_performance(train_score, test_score, train_size, test_size, cm_train, cm_test, classifier):
	"""
	Save all the important performance measures to the table performance
	"""

	print(create_or_delete_table('performance'))

	# Delete all existing documents with "classifier" of <classifier"

	r.table('performance').filter({
			'classifier': classifier
		}).delete().run(connection)


	# Insert the current data
	r.table('performance').insert({
			'classifier': classifier,
			'train_score': train_score,
			'train_size': train_size,
			'test_score': test_score,
			'test_size': test_size,
			'cm_train': cm_train.tolist(),
			'cm_test': cm_test.tolist()
		}).run(connection)

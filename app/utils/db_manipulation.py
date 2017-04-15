import rethinkdb as r

from app.lib.rethinkdb_connect import connection
from app.utils.rethinkdb_helpers import create_or_delete_table


def save_to_performance(data_size, train_score, test_score, train_size, test_size,
						cm_train, cm_test, f1_score, precision_score, recall_score,
						classifier, vocab_model, tf_idf, corrected):
	"""
	Save all the important performance measures to the table performance
	"""

	create_or_delete_table('performance')

	# Delete the row with the same data_size and classifier (that will serve as the unique identifier per row)
	r.table('performance').filter({
			'data_size': data_size,
			'classifier': classifier,
			'vocab_model': vocab_model,
			'tf_idf': tf_idf,
			'corrected': corrected
		}).delete().run(connection)

	# Insert the current data
	r.table('performance').insert({
			'data_size': data_size,
			'classifier': classifier,
			'vocab_model': vocab_model,
			'tf_idf': tf_idf,
			'corrected': corrected,
			'train_score': train_score,
			'train_size': train_size,
			'test_score': test_score,
			'test_size': test_size,
			'cm_train': cm_train.tolist(),
			'cm_test': cm_test.tolist(),
			'f1_score': f1_score,
			'precision_score': precision_score,
			'recall_score': recall_score
		}).run(connection)

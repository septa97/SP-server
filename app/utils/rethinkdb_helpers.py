import sys
import os
import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError

# from app.lib.rethinkdb_connect import connection

connection = r.connect('localhost', 28015, db='mooc')


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

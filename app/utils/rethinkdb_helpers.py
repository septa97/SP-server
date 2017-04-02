import sys
import os
import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError

from app.lib.rethinkdb_connect import connection


def create_or_delete_table(table, delete=False):
	try:
		r.table_create(table).run(connection)
		return 'Successfully created table <%s>.' % table
	except RqlRuntimeError:
		if delete:
			r.table(table).delete().run(connection)
			return 'Table <%s> already exists. Deleted all existing documents instead.' % table
		else:
			return 'Table <%s> already exists.' % table

import sys
import os
import langdetect
import rethinkdb as r

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/app/modules')
from preprocessor import is_English
sys.path.insert(0, dir_path + '/app/utils')
from rethinkdb_helpers import create_or_delete_table

connection = r.connect('localhost', 28015, db='mooc')


def main():
	cursor = r.table('reviews').run(connection)

	rows = []
	for document in cursor:
		rows.append(document)

	review_label_tuples = []
	total = 0
	for row in rows:
		reviews = row['data']
		labels = row['ratings']
		total += 1
		print('Preprocessing...', total*100/len(rows), '%', end='\r')

		for i in range(0, len(reviews)):
			if not is_English(reviews[i]):
				continue

			review_label_tuples.append((reviews[i], labels[i]))

	create_or_delete_table('combined_reviews_with_labels', delete=True)

	for i in range(0, len(review_label_tuples)):
		print('Writing to the database...', i*100//len(review_label_tuples), '%', end='\r')
		r.table('combined_reviews_with_labels').insert({
				'id': i,
				'data': review_label_tuples[i][0],
				'label': review_label_tuples[i][1]
			}).run(connection)

	print('Successfully changed review ratings to its corresponding labels.')


if __name__ == "__main__":
	main()

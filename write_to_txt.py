import shutil
import sys
import os
import rethinkdb as r

from textblob import TextBlob

connection = r.connect('localhost', 28015, db='mooc')


def not_corrected(path):
	data_path = os.path.dirname(os.path.realpath(__file__)) + path
	os.makedirs(data_path, exist_ok=True)

	classes = ['very_positive', 'positive', 'neutral', 'negative', 'very_negative']

	for c in classes:
		curr_dir = '%s/%s' % (data_path, c)

		if os.path.exists(curr_dir):
			shutil.rmtree(curr_dir)
			print('Deleted directory %s.' % curr_dir)

		os.makedirs(curr_dir)

	cursor = r.table('combined_reviews_with_labels').run(connection)
	very_positives = very_negatives = positives = negatives = neutrals = 0

	print('Writing to the text files...')
	for document in cursor:
		if document['label'] == 5:
			with open('%s/very_positive/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			very_positives += 1
		elif document['label'] == 4:
			with open('%s/positive/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			positives += 1
		elif document['label'] == 3:
			with open('%s/neutral/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			neutrals += 1
		elif document['label'] == 2:
			with open('%s/negative/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			negatives += 1
		elif document['label'] == 1:
			with open('%s/very_negative/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			very_negatives += 1


	print('very_positives:', very_positives)
	print('positives:', positives)
	print('neutrals:', neutrals)
	print('negatives:', negatives)
	print('very_negatives:', very_negatives)


def corrected(path):
	data_path = os.path.dirname(os.path.realpath(__file__)) + path
	os.makedirs(data_path, exist_ok=True)

	classes = ['very_positive', 'positive', 'neutral', 'negative', 'very_negative']

	for c in classes:
		curr_dir = '%s/%s' % (data_path, c)

		if os.path.exists(curr_dir):
			shutil.rmtree(curr_dir)
			print('Deleted directory %s.' % curr_dir)

		os.makedirs(curr_dir)

	cursor = r.table('combined_reviews_with_labels').run(connection)
	very_positives = very_negatives = positives = negatives = neutrals = 0

	print('Writing to the text files...')
	for document in cursor:
		document['data'] = str(TextBlob(document['data']).correct())

		if document['label'] == 5:
			with open('%s/very_positive/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			very_positives += 1
		elif document['label'] == 4:
			with open('%s/positive/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			positives += 1
		elif document['label'] == 3:
			with open('%s/neutral/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			neutrals += 1
		elif document['label'] == 2:
			with open('%s/negative/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			negatives += 1
		elif document['label'] == 1:
			with open('%s/very_negative/%s.txt' % (data_path, document['id']), 'w') as fp:
				fp.write(document['data'])

			very_negatives += 1


	print('very_positives:', very_positives)
	print('positives:', positives)
	print('neutrals:', neutrals)
	print('negatives:', negatives)
	print('very_negatives:', very_negatives)


if __name__ == "__main__":
	not_corrected('/app/data/reviews/not_corrected')
	corrected('/app/data/reviews/corrected')

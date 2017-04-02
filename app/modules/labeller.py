import sys
import os
import rethinkdb as r
import numpy as np

from rethinkdb.errors import RqlRuntimeError
from textblob import TextBlob

from app.lib.rethinkdb_connect import connection


class Labeller:
	def __init__(self, reviews):
		self.reviews = reviews

	def textblob_label(self):
		"""
		Label the course reviews using the TextBlob module
		"""

		combined_reviews_with_labels = []

		for review in self.reviews:
			tb = TextBlob(review[1])

			if tb.sentiment.subjectivity == 0:
				combined_reviews_with_labels.append((review[0], review[1], 0))
			elif tb.sentiment.polarity < 0:
				combined_reviews_with_labels.append((review[0], review[1], -1))
			elif tb.sentiment.polarity > 0:
				combined_reviews_with_labels.append((review[0], review[1], 1))
			else:
				combined_reviews_with_labels.append((review[0], review[1], 0))

		return combined_reviews_with_labels

	def verb_adj_label(self):
		"""
		Label the course reviews using SentiWordNet. Verbs and adjectives will only be considered
		"""

		return 'Not yet implemented'

	def all_pos_label(self):
		"""
		Label the course reviews using SentiWordNet. All parts-of-speech will be considered
		"""

		return 'Not yet implemented'


def main():
	cursor = r.table('combined_reviews').run(connection)
	reviews = [(document['id'], document['data']) for document in cursor]

	labeller = Labeller(reviews)
	results = labeller.textblob_label()

	for result in results:
		r.table('combined_reviews').filter({
				'id': result[0]
			}).update({
				'label': result[2]
			}).run(connection)


if __name__ == "__main__":
	main()

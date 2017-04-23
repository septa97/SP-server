import shutil
import sys
import os

from sklearn.externals import joblib

dir_path = os.path.dirname(os.path.realpath(__file__))


def persist_to_disk(classifier, vocab_model, tf_idf, corrected, clf, vocabulary):
	curr_dir = '%s/../data/models/%s/%s/%s/%s' % (dir_path, classifier, vocab_model,
													'tf_idf' if tf_idf else 'not_tf_idf',
													'corrected' if corrected else 'not_corrected')

	if os.path.exists(curr_dir):
		shutil.rmtree(curr_dir)
		print('Deleted directory %s.' % curr_dir)

	os.makedirs(curr_dir)

	joblib.dump(clf, curr_dir + '/clf.pkl')
	joblib.dump(vocabulary, curr_dir + '/vocabulary.pkl')


def load_clf_and_vocabulary(classifier, vocab_model, tf_idf, corrected):
	curr_dir = '%s/../data/models/%s/%s/%s/%s' % (dir_path, classifier, vocab_model,
													'tf_idf' if tf_idf else 'not_tf_idf',
													'corrected' if corrected else 'not_corrected')

	clf = joblib.load(curr_dir + '/clf.pkl')
	vocabulary = joblib.load(curr_dir + '/vocabulary.pkl')

	return clf, vocabulary

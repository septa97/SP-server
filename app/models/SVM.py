import sys
import os
import numpy as np
import rethinkdb as r
import matplotlib.pyplot as plt
import mpld3

from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA, SparsePCA, KernelPCA
from sklearn.cluster import FeatureAgglomeration
from sklearn.manifold import TSNE
from sklearn.metrics import confusion_matrix
from sklearn import svm

# dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, dir_path + "/../utils")
# sys.path.insert(0, dir_path + "/../modules")
# from data_manipulation import feature_scale, train_test_split
# from data_operation import accuracy_score
# from data_plotting import plot_confusion_matrix
# from config import config
from app.lib.rethinkdb_connect import connection
from app.utils.data_manipulation import feature_scale, train_test_split
from app.utils.data_operation import accuracy_score
from app.utils.data_plotting import plot_confusion_matrix
from app.configuration.config import config


def main(test_size=0.2):
	X = np.empty([0, config['VOCAB_SIZE']])
	y = np.array([])

	# Load X and y
	X = np.array(r.db(config['DB_NAME']).table('X').nth(0).run(connection)['X'])
	y = np.array(r.db(config['DB_NAME']).table('y').nth(0).run(connection)['y'])

	# Split the data into training and testing set
	X_train, X_test, y_train, y_test = train_test_split(X, y)

	# t-Distributed Stochastic Neighbor Embedding
	tsne = TSNE(n_components=2, init='pca', random_state=0)
	Xtsne_train_reduced = tsne.fit_transform(X_train)

	# Principal Component Analysis
	pca = PCA(n_components=2)
	Xpca_train_reduced = pca.fit_transform(X_train)

	# Support Vector Classifier (one vs rest strategy, RBF/Gaussian kernel)
	clf = svm.SVC(C=1, decision_function_shape='ovr', kernel='rbf', verbose=True)
	clf.fit(X_train, y_train)

	training_score = clf.score(X_train, y_train)
	test_score = clf.score(X_test, y_test)

	print('(sklearn) Training data accuracy:', training_score)
	print('(sklearn) Test data accuracy:', test_score)

	target_names = ['Negative', 'Neutral', 'Positive']
	colors = ['navy', 'turquoise', 'darkorange']

	# p = figure(title="t-distributed stochastic neighbor embedding (t-SNE)", x_axis_label='x', y_axis_label='y')
	# for color, i, target_name in zip(colors, [-1, 0, 1], target_names):
	# 	p.scatter(Xtsne_train_reduced[y_train == i, 0], Xtsne_train_reduced[y_train == i, 1], color=color)

	# show(p)

	# Plot using Bokeh
	TOOLS = "pan,wheel_zoom,box_zoom,reset,hover,save"
	p = figure(title="Principal Component Analysis (PCA)", x_axis_label='x', y_axis_label='y', tools=TOOLS)
	for color, i, target_name in zip(colors, [-1, 0, 1], target_names):
		p.scatter(Xpca_train_reduced[y_train == i, 0], Xpca_train_reduced[y_train == i, 1], color=color)

	script, div = components(p, wrap_script=False, wrap_plot_info=True)

	return script, div, training_score, test_score

	# show(p)

	# Compute and plot the confusion matrix
	# plt.figure()
	# cnf_matrix = confusion_matrix(y_test, clf.predict(X_test))
	# plot_confusion_matrix(cnf_matrix, target_names, title='Confusion matrix, without normalization')
	# mpld3.show()


if __name__ == "__main__":
	main()

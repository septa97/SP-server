import requests


def main():
	min_df = 5
	# data_sizes = [10000, 30000, 50000, 70000, 90000, 100000, -1]
	data_sizes = [-1]
	# classifiers = ['LR', 'SVM', 'MLP']
	classifiers = ['SVM']
	# vocab_models = ['unigram', 'bigram', 'trigram']
	vocab_models = ['trigram']
	tf_idfs = [True, False]
	corrected = [True, False]

	res_count = 0

	for d in data_sizes:
		for clf in classifiers:
			for v in vocab_models:
				for t in tf_idfs:
					for c in corrected:
						payload = {
							'minDF': min_df,
							'classifier': clf,
							'dataSize': d,
							'vocabModel': v,
							'tfIdf': t,
							'corrected': c
						}

						headers = {
            				'Content-Type': 'application/x-www-form-urlencoded'
						}

						print('Training with data size %s, using %s and %s and %s, and %s. %s/%s' % (d, clf, v, t, c, res_count+1, len(data_sizes) * len(classifiers) * len(vocab_models) * len(tf_idfs) * len(corrected)))
						requests.post('http://localhost:5000/api/v1/classifier/train', json=payload, headers=headers)
						res_count += 1


	print('Total number of requests:', res_count)


if __name__ == "__main__":
	main()

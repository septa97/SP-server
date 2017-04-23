import requests


def main():
	min_df = 5
	# data_sizes = [-1, 1000, 5000, 10000, 20000, 30000, 40000]
	data_sizes = [-1]
	# classifiers = ['LR', 'SVM', 'MLP']
	classifiers = ['SVM', 'MLP']
	vocab_models = ['unigram', 'bigram', 'trigram']
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

						requests.post('http://localhost:5000/api/v1/classifier/train', json=payload, headers=headers)
						res_count += 1


	print('Total number of requests:', res_count)


if __name__ == "__main__":
	main()

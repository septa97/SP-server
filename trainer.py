import requests


def main():
	min_df = 5
	classifiers = ['LR', 'SVM', 'MLP']
	data_sizes = [1000, 2000, 5000, 10000, 15000, 20000, -1]
	vocab_models = ['unigram', 'bigram', 'trigram']
	tf_idfs = [True, False]
	corrected = [True, False]

	res = []

	for clf in classifiers:
		for d in data_sizes:
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

						curr_res = requests.post('http://localhost:5000/api/v1/classifier/train', json=payload, headers=headers)
						print(curr_res.text)
						res.append(curr_res)


	print('Total number of requests:', len(res))


if __name__ == "__main__":
	main()

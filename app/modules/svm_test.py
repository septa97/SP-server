import pandas as pd
from sklearn import svm

X = pd.read_csv('X_temp.csv')
y = pd.read_csv('y_temp.csv')

X_train = X[0:800]
X_test = X[800:]
y_train = y[0:800]
y_test = y[800:]

clf = svm.SVC(decision_function_shape='ovr', verbose=True)
print(X_train.shape)
print(y_train.shape)

clf.fit(X_train, y_train.values)
training_score = clf.score(X_train.values, y_train.values)
test_score = clf.score(X_test.values, y_test.values)

print('Training data accuracy:', training_score)
print('Test data accuracy:', test_score)

import sys
import os
import rethinkdb as r

from flask import Blueprint, jsonify, request
from app.configuration.config import config
from app.models.LR import main as LogisticRegression
from app.models.SVM import main as SupportVectorMachine
from app.models.MLP import main as MultiLayerPerceptron
from app.utils.db_manipulation import save_to_accuracy


mod = Blueprint('classifier', __name__)

@mod.route('/train', methods=['POST'])
def train_LR():
	data = request.get_json(force=True)

	if (data['classifier'] == 'LR'):
		training_score, test_score, training_size = LogisticRegression(test_size=data['testDataSize'])
		save_to_accuracy(training_score, test_score, training_size, 'LR')
		return jsonify({'message': 'Done training using Logistic Regression. You can view the visualization in the Visualization tab later.'})
	elif (data['classifier'] == 'SVM'):
		training_score, test_score, training_size = SupportVectorMachine(test_size=data['testDataSize'])
		save_to_accuracy(training_score, test_score, training_size, 'SVM')
		return jsonify({'message': 'Done training using Support Vector Machine. You can view the visualization in the Visualization tab later.'})
	else:
		training_score, test_score, training_size = MultiLayerPerceptron(test_size=data['testDataSize'])
		save_to_accuracy(training_score, test_score, training_size, 'MLP')
		return jsonify({'message': 'Done training using Multi-layer Perceptron. You can view the visualization in the Visualization tab later.'})

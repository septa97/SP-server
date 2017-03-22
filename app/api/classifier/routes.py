import sys
import os
import rethinkdb as r

from flask import Blueprint, jsonify, request
from app.configuration.config import config
from app.models.LR import main as LogisticRegression
from app.models.SVM import main as SupportVectorMachine
from app.models.MLP import main as MultiLayerPerceptron
from app.lib.rethinkdb import connection
from app.utils.db_manipulation import save_to_LR, save_to_SVM, save_to_MLP


DB_NAME = config['DB_NAME']
mod = Blueprint('classifier', __name__)

@mod.route('/logistic-regression', methods=['POST'])
def train_LR():
	data = request.get_json(force=True)
	script, div, training_score, test_score, training_size = LogisticRegression(test_size=data['testDataSize'])
	save_to_LR(script, div, training_score, test_score, training_size)

	return jsonify({'message': 'Done training using Logistic Regression. You can view the visualization in the Visualization tab later.'})


@mod.route('/support-vector-machine', methods=['POST'])
def train_SVM():
	data = request.get_json(force=True)
	script, div, training_score, test_score, training_size = SupportVectorMachine(test_size=data['testDataSize'])
	save_to_SVM(script, div, training_score, test_score, training_size)

	return jsonify({'message': 'Done training using Support Vector Machine. You can view the visualization in the Visualization tab later.'})


@mod.route('/multi-layer-perceptron', methods=['POST'])
def train_MLP():
	data = request.get_json(force=True)
	script, div, training_score, test_score, training_size = MultiLayerPerceptron(test_size=data['testDataSize'])
	save_to_MLP(script, div, training_score, test_score, training_size)

	return jsonify({'message': 'Done training using Multi-layer Perceptron. You can view the visualization in the Visualization tab later.'})

import os
from flask import Flask
from flask_cors import CORS, cross_origin
from app.config import config

def create_app(env):
	app = Flask(__name__)
	CORS(app)
	app.config.from_object(config[env])

	@app.route('/')
	def index():
		return 'Hello World!'

	return app

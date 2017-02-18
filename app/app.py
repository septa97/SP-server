import os
from flask import Flask
from app.config import config

def create_app(env):
	app = Flask(__name__)
	app.config.from_object(config[env])
	
	@app.route('/')
	def index():
		return 'Hello World!'

	return app
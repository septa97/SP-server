import os
from flask import Flask, render_template
from flask_assets import Environment, Bundle
from app.config import config

def create_app(env):
	app = Flask(__name__)
	assets = Environment(app)
	js = Bundle('js/*.js', output='gen/packed.js')
	assets.register('js_all', js)

	app.config.from_object(config[env])
	
	@app.route('/')
	def index():
		return render_template('index.html')

	return app
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import config


def create_app(env):
	app = Flask(__name__)
	app.config.from_object(config[env])

	# Naive CORS
	CORS(app)
	load_blueprints(app)

	# Catch-All URL
	@app.route('/', defaults={'path': ''})
	@app.route('/<path:path>')
	def catch_all(path):
		return jsonify(message='Invalid route :(')

	return app


def load_blueprints(app):
	from .api.coursera.routes import mod as coursera_mod
	from .api.rethinkdb.routes import mod as rethinkdb_mod
	from .api.classifier.routes import mod as classifier_mod
	from .api.dimensionality_reduction.routes import mod as dimensionality_reduction_mod
	# from .api.scraper.routes import mod as scraper_mod

	app.register_blueprint(coursera_mod, url_prefix='/api/v1/coursera')
	app.register_blueprint(rethinkdb_mod, url_prefix='/api/v1/rethinkdb')
	app.register_blueprint(classifier_mod, url_prefix='/api/v1/classifier')
	app.register_blueprint(dimensionality_reduction_mod, url_prefix='/api/v1/dimensionality-reduction')
	# app.register_blueprint(scraper_mod, url_prefix='/api/v1/scraper')

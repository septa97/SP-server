import rethinkdb as r

from flask import Blueprint, jsonify

from app.lib.rethinkdb_connect import connection
from app.modules.scraper import CourseraScraper


mod = Blueprint('scraper', __name__)

@mod.route('/scrape-all', methods=['GET'])
def scrape_all():
	paths = {
		'slugs': os.path.dirname(os.path.realpath(__file__)) + '/../../data/slugs.json',
		'scraped': os.path.dirname(os.path.realpath(__file__)) + '/../../data/real_scraped.json'
	}

	scraper = CourseraScraper('https://www.coursera.org/learn/', paths)
	# scraper.start()

	return jsonify({'message': 'Successfully scraped all the reviews in all the courses.'})

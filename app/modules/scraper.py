import sys
import os
import time
import json
import rethinkdb as r

from rethinkdb.errors import RqlRuntimeError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

# from app.configuration.config import config
# from app.lib.rethinkdb_connect import connection
# from app.utils.rethinkdb_helpers import create_or_delete_table
dir_path = os.path.dirname(os.path.realpath(__file__))
# sys.path.insert(0, dir_path + '/../configuration')
# from config import config
# sys.path.insert(0, dir_path + '/../lib')
# from rethinkdb_connect import connection
# sys.path.insert(0, dir_path + '/../utils')
# from rethinkdb_helpers import create_or_delete_table

config = {
	'HOST': 'localhost',
	'PORT': 28015,
	'DB_NAME': 'mooc'
}

connection = r.connect(config['HOST'], config['PORT'], db=config['DB_NAME'])


class CourseraScraper:
	def __init__(self, base_url, paths, driver=webdriver.Firefox(), max_wait_time=60):
		self.base_url = base_url
		self.driver = driver
		self.wait = WebDriverWait(driver, max_wait_time)
		self.actions = ActionChains(driver)
		self.overall_reviews = 0
		self.load_slugs_json(paths['slugs'])
		self.load_scraped_json(paths['scraped'])
		self.load_number_of_reviews_json(paths['number_of_reviews'])
		self.init_connection()


	def start(self):
		"""
		Start the scraping
		"""
		for slug in self.slugs['elements']:
			# if slug not in self.scraped['elements']:
			if (slug not in self.number_of_reviews) \
				or (self.number_of_reviews[slug] != -1 and
				self.number_of_reviews[slug]['expected'] != self.number_of_reviews[slug]['actual']):

				result = self.scrape_reviews(slug)

				if result == -1:
					self.number_of_reviews[slug] = -1

				if slug not in self.scraped['elements']:
					self.scraped['elements'].append(slug)

				# Write to file everytime a course is scraped
				dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../data'
				os.makedirs(dir_path, exist_ok=True)
				with open(dir_path + '/scraped.json', 'w') as fp:
					json.dump(self.scraped, fp, indent=2)

				with open(dir_path + '/number_of_reviews.json', 'w') as fp:
					json.dump(self.number_of_reviews, fp, indent=2)

				print(slug, 'is written to scraped.json...')
			else:
				print(self.base_url + slug, 'is already scraped...')

		print('Overall total number of reviews fetched:', str(self.overall_reviews))
		self.driver.close()


	def load_slugs_json(self, path):
		"""
		Loads the courses information that was fetched from the Coursera's Catalog API
		"""
		with open(path) as json_data:
			self.slugs = json.load(json_data)


	def load_scraped_json(self, path):
		"""
		Loads the list of already scraped courses
		"""
		with open(path) as json_data:
			self.scraped = json.load(json_data)


	def load_number_of_reviews_json(self, path):
		"""
		Loads the list of courses and its expected and actual number of reviews
		"""
		with open(path) as json_data:
			self.number_of_reviews = json.load(json_data)


	def init_connection(self):
		"""
		Initializes the connection to the RethinkDB server
		"""
		try:
			r.db_create(config['DB_NAME']).run(connection)
			print('Successfully created database %s.' % config['DB_NAME'])
		except RqlRuntimeError:
			print('Database', config['DB_NAME'], 'already exists.')

		# create_or_delete_table('reviews')


	def scrape_reviews(self, slug):
		"""
		Scrapes all the reviews (if there is a review in that course) in the specified url
		and then insert it to the database
		"""
		print('Scraping ' + self.base_url + slug + '...')
		reviews = {
			'id': slug,
			'data': [],
			'ratings': []
		}

		self.driver.get(self.base_url + slug)
		try:
			elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-track-component="view_all_reviews"]')))
		except TimeoutException:
			# Will return if there are no reviews in the course
			print(slug, 'has no reviews.')
			return -1

		# Wait for 5 seconds before clicking the "See all reviews" button
		time.sleep(5)
		elem.click()

		# Wait for the modal that contains the reviews to be visible
		elem = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'c-modal-content')))
		# Set the focus to the modal
		self.actions.move_to_element(elem)

		# Wait for 5 seconds before triggering the infinite scrolling
		time.sleep(5)
		elem.send_keys(Keys.END)
		curr = len(self.driver.find_elements_by_class_name('rc-CourseReview'))
		time.sleep(5)

		# Expected number of reviews in the course (if there is)
		expected_reviews = self.driver.find_element_by_class_name('rc-CountHeader') \
							.find_element_by_class_name('c-value') \
							.find_element_by_tag_name('span').text

		expected_reviews = int(expected_reviews.replace(',', ''))

		while curr < expected_reviews:
			elem.send_keys(Keys.END)
			curr = len(self.driver.find_elements_by_class_name('rc-CourseReview'))
			print('Expected: %s, Current: %s' % (expected_reviews, curr), end='\r')
			# try:
			# 	self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'spinner')))
			# except TimeoutException:
			# 	# If waiting exceeds the timeout, it means that all reviews are now in the modal
			# 	break

			# self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'spinner')))


		total_reviews = 0
		divs = self.driver.find_elements_by_class_name('rc-CourseReview')

		for div in divs:
			# Extract the text
			paragraphs = div.find_element_by_tag_name('div') \
							.find_element_by_class_name('rc-CML') \
							.find_element_by_tag_name('div') \
							.find_elements_by_tag_name('p')

			review = ''
			for paragraph in paragraphs:
				review += paragraph.text

			reviews['data'].append(review)

			total_reviews += 1
			self.overall_reviews += 1

			# Extract the reviews
			stars = div.find_element_by_tag_name('div') \
						.find_element_by_class_name('rc-CourseRatingIcons') \
						.find_elements_by_class_name('cif-star')

			reviews['ratings'].append(len(stars))

		# Insert/Update to the table 'reviews' of the database 'mooc'
		cursor = r.table('reviews').filter({
				'id': slug
			}).run(connection)

		i = 0
		for document in cursor:
			i += 1

		if i == 0:
			r.table('reviews').insert(reviews).run(connection)
		else:
			r.table('reviews').filter({
					'id': slug
				}).update(reviews).run(connection)

		print('Reviews for', slug, 'was added to database:', config['DB_NAME'] + ', table: reviews')
		print('Expected number of reviews: %s. Total number of reviews scraped: %s' % (expected_reviews, total_reviews))

		self.number_of_reviews[slug] = {
			'expected': expected_reviews,
			'actual': total_reviews
		}


if __name__ == "__main__":
	dir_path = os.path.dirname(os.path.realpath(__file__))

	paths = {
		'slugs': dir_path + '/../data/slugs.json',
		'scraped': dir_path + '/../data/scraped.json',
		'number_of_reviews': dir_path + '/../data/number_of_reviews.json'
	}

	scraper = CourseraScraper('https://www.coursera.org/learn/', paths)
	scraper.start()

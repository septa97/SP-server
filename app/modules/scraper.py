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
sys.path.insert(0, dir_path + '/../configuration')
from config import config
sys.path.insert(0, dir_path + '/../lib')
from rethinkdb_connect import connection
sys.path.insert(0, dir_path + '/../utils')
from rethinkdb_helpers import create_or_delete_table


class CourseraScraper:
	def __init__(self, base_url, paths, driver=webdriver.Firefox(), max_wait_time=60):
		self.base_url = base_url
		self.driver = driver
		self.wait = WebDriverWait(driver, max_wait_time)
		self.actions = ActionChains(driver)
		self.overall_reviews = 0
		self.load_slugs_json(paths['slugs'])
		self.load_scraped_json(paths['scraped'])
		self.init_connection()


	def start(self):
		"""
		Start the scraping
		"""
		for slug in self.slugs['elements']:
			if slug not in self.scraped['elements']:
				self.scrape_reviews(slug)
				self.scraped['elements'].append(slug)

				# Write to file everytime a course is scraped
				dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../data'
				os.makedirs(dir_path, exist_ok=True)
				with open(dir_path + '/real_scraped.json', 'w') as fp:
					json.dump(self.scraped, fp, indent=2)

				print(slug, 'is written to real_scraped.json...')
			else:
				print(self.base_url + slug, 'is already scraped...')

		print('Overall total number of reviews fetched:', str(self.overall_reviews))
		driver.close()


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


	def init_connection(self):
		"""
		Initializes the connection to the RethinkDB server
		"""
		try:
			r.db_create(config['DB_NAME']).run(connection)
			print('Successfully created database %s.' % config['DB_NAME'])
		except RqlRuntimeError:
			print('Database', config['DB_NAME'], 'already exists.')

		print(create_or_delete_table('reviews'))


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
			return

		# Wait for 5 seconds before clicking the "See all reviews" button
		time.sleep(5)
		elem.click()

		# Wait for the modal that contains the reviews to be visible
		elem = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'c-modal-content')))
		# Set the focus to the modal
		self.actions.move_to_element(elem)


		# Wait for 5 seconds before triggering the infinite scrolling
		time.sleep(5)
		while True:
			elem.send_keys(Keys.END)
			try:
				self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'spinner')))
			except TimeoutException:
				# If waiting exceeds the timeout, it means that all reviews are now in the modal
				break

			self.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'spinner')))


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

		# Insert to the table 'reviews' of the database 'mooc'
		r.table('reviews').insert(reviews).run(connection)
		print('Reviews for', slug, 'was added to database:', config['DB_NAME'] + ', table: reviews')
		print('Total reviews:', str(total_reviews))


if __name__ == "__main__":
	paths = {
		'slugs': os.path.dirname(os.path.realpath(__file__)) + '/../data/slugs.json',
		'scraped': os.path.dirname(os.path.realpath(__file__)) + '/../data/real_scraped.json'
	}

	scraper = CourseraScraper('https://www.coursera.org/learn/', paths)
	scraper.start()

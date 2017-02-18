import time
import json
import os
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from config import config

# Globals
base_url = 'https://www.coursera.org/learn/';
driver = webdriver.Firefox()
wait = WebDriverWait(driver, 60)	# 60 seconds maximum wait time for explicit waits
actions = ActionChains(driver)
paths = {
	'slugs': os.path.dirname(os.path.realpath(__file__)) + '/../data/slugs.json',
	'scraped': os.path.dirname(os.path.realpath(__file__)) + '/../data/scraped.json'
}
global_total_reviews = 0

# Function that scrapes all the reviews (if there is a review in that course) in the specified url and then insert it to the database
# Input: slug of the course, connection object
# Output: N/A
def scrape_reviews(slug, connection):
	global global_total_reviews
	print('Scraping ' + base_url + slug + '...')
	reviews = {slug: []}

	driver.get(base_url + slug)
	try:
		elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-track-component="view_all_reviews"]')))
	except TimeoutException:
		# Will return if there are no reviews in the course
		print(slug, 'has no reviews.')
		return

	# Wait for 5 seconds before clicking the "See all reviews" button
	time.sleep(5)
	elem.click()

	# Wait for the modal that contains the reviews to be visible
	elem = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'c-modal-content')))
	# Set the focus to the modal
	actions.move_to_element(elem)


	# Wait for 5 seconds before triggering the infinite scrolling
	time.sleep(5)
	while True:
		elem.send_keys(Keys.END)
		try:
			wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'spinner')))
		except TimeoutException:
			# If waiting exceeds the timeout, it means that all reviews are now in the modal
			break

		wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'spinner')))


	total_reviews = 0	
	divs = driver.find_elements_by_class_name('rc-CML')
	for div in divs:
		paragraphs = div.find_element_by_tag_name('div').find_elements_by_tag_name('p')

		review = ''
		for paragraph in paragraphs:
			review += paragraph.text
		
		reviews[slug].append(review)

		total_reviews += 1
		global_total_reviews += 1

	# Insert to the table 'reviews' of the database 'mooc'
	r.db(config['DB_NAME']).table('reviews').insert(reviews).run(connection)
	print('Reviews for', slug, 'was added to database:', config['DB_NAME'] + ', table: reviews')
	print('Total reviews:', str(total_reviews))


# Function that initializes the connection to the RethinkDB server
# Input: N/A
# Output: connection object
def init_connection():
	connection = r.connect(config['HOST'], config['PORT'])
	try:
		r.db_create(config['DB_NAME']).run(connection)
		print('Database', config['DB_NAME'], 'is now created.')
	except RqlRuntimeError:
		print('Database', config['DB_NAME'], 'already exists.')

	try:
		r.db(config['DB_NAME']).table_create('reviews').run(connection)
		print('reviews table has been created.')
	except RqlRuntimeError:
		print('Table reviews already exists.')
	finally:
		return connection


# Function that loads the courses information that was fetched from the Coursera's Catalog API
# Input: path of slugs.json
# Output: data of slugs.json
def load_slugs_json(path):
	with open(path) as json_data:
		return json.load(json_data)

# Function that loads the list of already scraped courses
# Input: path of scraped.json
# Output: data of scraped.json
def load_scraped_json(path):
	with open(path) as json_data:
		return json.load(json_data)

# Function that triggers the start the scraping
# Input: N/A
# Output: N/A
def start():
	connection = init_connection()
	slugs = load_slugs_json(paths['slugs'])
	scraped = load_scraped_json(paths['scraped'])

	for slug in slugs['elements']:
		if (slug not in scraped['elements']):
			scrape_reviews(slug, connection)
			scraped['elements'].append(slug)
			
			# Write to file everytime a course is scraped
			dir_path = os.path.dirname(os.path.realpath(__file__)) + '/../data';
			os.makedirs(dir_path, exist_ok=True)
			with open(dir_path + '/scraped.json', 'w') as fp:
				json.dump(scraped, fp)

			print(slug, 'is written to scraped.json...')
		else:
			print(base_url + slug, 'is already scraped...')
	
	print('Overall total number of reviews fetched:', str(global_total_reviews))
	driver.close()


start()

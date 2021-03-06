Coursera's MOOCs Sentiment Analysis: Dimensionality Reduction Visualization and Model Prediction Explanation (server)
=====================================================================================================================

## Modules
* Data Scraper
* Database (RethinkDB)
* Cron job
* Sentiment Analyzer

## Tech stack
* Frontend - Vue.js, Google Maps API, dc.js, d3.js
* Server-side - Node.js OR Python-based framework
* Machine Learning - scikit-learn OR/AND tensorflow

## Python modules
* langdetect
* nltk
* numpy
* scipy
* pandas
* virtualenv
* scikit-learn
* rethinkdb
* selenium
* bokeh
* mpld3

## Prerequisites
* Python version 3.3 or higher
* pip (Python package manager, install depending on your OS)
``` bash
sudo pip install -U pip virtualenv
```

## Installation (execute from the project root folder)
``` bash
virtualenv venv
. venv/bin/activate
pip install --editable .
pip install -r requirements.txt
```

## Download data.zip from this link and extract inside the app folder
[https://goo.gl/ZKXxkK](https://goo.gl/ZKXxkK)
The data on the link above also has the trained models.

You can view the raw data that was scraped from the Coursera website here: [https://www.kaggle.com/septa97/100k-courseras-course-reviews-dataset](https://www.kaggle.com/septa97/100k-courseras-course-reviews-dataset)

## Running the application
``` bash
./run.sh
```

**The server is now serving on localhost:5000**

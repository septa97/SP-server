import sys
import os
import rethinkdb as r

from app.configuration.config import config


connection = r.connect(host=config['HOST'], port=config['PORT'], db=config['DB_NAME'])

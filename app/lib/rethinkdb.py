import rethinkdb as r
from app.configuration.config import config


connection = r.connect(config['HOST'], config['PORT'])

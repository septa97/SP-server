import rethinkdb as r
# from app.configuration.config import config
config = {
	'HOST': 'localhost',
	'PORT': 28015,
	'DB_NAME': 'mooc',
	'VOCAB_SIZE': 500
}


connection = r.connect(config['HOST'], config['PORT'])

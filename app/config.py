class Config:
	DEBUG = False
	TESTING = False

class DevelopmentConfig(Config):
	DEBUG = True

class TestingConfig(Config):
	TESTING = True

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig
}
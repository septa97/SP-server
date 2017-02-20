import rethinkdb as r
from app.modules.config import config

HOST = config['HOST']
PORT = config['PORT']
connection = r.connect(HOST, PORT)

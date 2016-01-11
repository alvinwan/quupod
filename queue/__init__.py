"""
Main Queue Launch

@author: Alvin Wan, Ben Kha
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# parse configuration file
try:
    lines = filter(bool, open('queue.cfg').read().splitlines())
    config = dict(map(lambda s: s.strip(), d.split(':')) for d in lines)
    settings = (config['username'],
        config['password'],
        config['server'],
        config['database'])
    secret_key = config['secret_key']
except FileNotFoundError:
    raise UserWarning('Configuration file not found. Rerun `make install` and \
    update the new queue.cfg accordingly.')
except KeyError:
    raise UserWarning('queue.cfg is missing critical information. All of the \
following must be present: username, password, server, database, secret_key')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % settings
db = SQLAlchemy(app)

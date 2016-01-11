from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# parse configuration file
try:
    lines = filter(bool, open('queue.cfg').read().splitlines())
    db = tuple(d.split(':')[1].strip() for d in lines)
except FileNotFoundError:
    raise UserWarning('Configuration file not found. Rerun `make install`.')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % db
db = SQLAlchemy(app)

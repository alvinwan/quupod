from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import flask_login
import os

# Extract information from environment.
get = lambda v, default: os.environ.get(v, default)

database_url = get('DATABASE_URL', 'mysql://root:root@localhost/queue')
url = urlparse(database_url)
config = {
    'NAME': url.path[1:],
    'USERNAME': url.username,
    'PASSWORD': url.password,
    'HOST': url.hostname,
    'PORT': url.port,
    'DATABASE': database_url.split('/')[3].split('?')[0],
    'SECRET_KEY': get('SECRET_KEY', 'dEf@u1t$eCRE+KEY'),
    'DEBUG': get('DEBUG', False),
    'WHITELIST': get('WHITELIST', ''),
    'GOOGLECLIENTID': get('GOOGLECLIENTID', None)
}
try:
    lines = filter(bool, open('config.cfg').read().splitlines())
    config.update(dict(filter(
        lambda item: item[1],
        (map(lambda s: s.strip(), d.split(':')) for d in lines))))
except FileNotFoundError:
    print(' * Configuration file not found. Rerun `make install` and \
update the new config.cfg accordingly.')
    if not (config['HOST'] and config['USERNAME'] and config['DATABASE']):
        raise UserWarning('Environment variables do not supply database \
credentials, and configuration file is missing.')
except KeyError:
    raise UserWarning('config.cfg is missing critical information that is not \
found in the environment. All of the following must be present: username, \
password, server, database, secret_key, debug')

secret_key = config['SECRET_KEY']
debug = bool(config['DEBUG'])
whitelist = config['WHITELIST'].split(',')
googleclientID = config['GOOGLECLIENTID']

# Flask app
app = Flask(__name__)

# Configuration for mySQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}'.format(**config)
db = SQLAlchemy(app)

# Configuration for login sessions
app.secret_key = secret_key
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Configuration for app views
from .public.views import public
from .admin.views import admin

blueprints = (public, admin)
for blueprint in blueprints:
    print(' * Registering blueprint "%s"' % blueprint.name)
    app.register_blueprint(blueprint)

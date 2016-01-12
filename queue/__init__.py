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
    debug = bool(config['debug'])
except FileNotFoundError:
    raise UserWarning('Configuration file not found. Rerun `make install` and \
    update the new queue.cfg accordingly.')
except KeyError:
    raise UserWarning('queue.cfg is missing critical information. All of the \
following must be present: username, password, server, database, secret_key, \
debug')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s' % settings
db = SQLAlchemy(app)

from .public.views import public
from .staff.views import staff

blueprints = (public, staff)

for blueprint in blueprints:
    print(' * Registering blueprint "%s"' % blueprint.name)
    app.register_blueprint(blueprint)

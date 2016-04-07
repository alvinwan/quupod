from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import flask_login
from flask_login import AnonymousUserMixin
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_socketio import SocketIO
import eventlet
import os
from .config import config, secret_key, debug, whitelist, googleclientID, port,\
    domain, tz

print(' * Running in DEBUG mode.' if debug else
      ' * Running in PRODUCTION mode.')

print(' * Google Client ID: %s' % googleclientID if googleclientID else
      ' * No Google Client ID found.')

# Flask app
app = Flask(__name__)

# Async socket initialization
eventlet.monkey_patch()
socketio = SocketIO(app, async_mode='eventlet')
thread = None

# Configuration for mySQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}'.format(**config)
db = SQLAlchemy(app)

# Configuration for login sessions
app.secret_key = secret_key
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Database migration management
migrate = Migrate(app, db)
migration_manager = Manager(app)

# Configuration for app views
from .public.views import public
from .queue.views import queue
from .admin.views import admin
from .dashboard.views import dashboard

blueprints = (public, admin, queue, dashboard)
for blueprint in blueprints:
    print(' * Registering blueprint "%s"' % blueprint.name)
    app.register_blueprint(blueprint)

# subdomain routes with special urls
app.register_blueprint(admin, url_prefix='/subdomain/<string:queue_url>/admin')
app.register_blueprint(queue, url_prefix='/subdomain/<string:queue_url>')

# Anonymous User definition
class Anonymous(AnonymousUserMixin):

    def can(self, *permission):
        return False

login_manager.anonymous_user = Anonymous

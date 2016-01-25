from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import flask_login
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import os
from .config import config, secret_key, debug, whitelist, googleclientID

print(' * Running in DEBUG mode.' if debug else
      ' * Running in PRODUCTION mode.')

print(' * Google Client ID: %s' % googleclientID if googleclientID else
      ' * No Google Client ID found.')

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

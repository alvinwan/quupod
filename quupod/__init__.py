"""Quupod application factory."""

from flask import Flask
from .models import db
from .models import migrate
from .models import migration_manager
from .models import toolbar
from .views import login_manager
from .views import socketio
from .views import error_not_found
from .views import error_server
import eventlet

CONFIG_PATH_FORMAT = '%s.config.%s'


# Flask app
app = Flask(__name__)
app.config.from_object(CONFIG_PATH_FORMAT % ('quupod', 'DevelopmentConfig'))

print(
    ' * Running in DEBUG mode.' if app.config['INIT']['debug'] else
    ' * Running in PRODUCTION mode.')

print(
    ' * Google Client ID: %s' % app.config['GOOGLECLIENTID']
    if app.config['GOOGLECLIENTID'] else ' * No Google Client ID found.')

# Async socket initialization
eventlet.monkey_patch()
socketio.init_app(app)

# Configuration for mySQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = \
    app.config['DATABASE_URL'].replace('mysql', 'mysql+pymysql', 1)
db.init_app(app)

# Configuration for login sessions
app.secret_key = app.config['SECRET_KEY']
login_manager.init_app(app)

# Flask Debug Toolbar
toolbar.init_app(app)

# Database migration management
migrate.init_app(app, db)
migration_manager(app)

from .public.views import public
from .queue.views import queue
from .admin.views import admin
from .dashboard.views import dashboard

BLUEPRINTS = [public, queue, admin, dashboard]

for blueprint in BLUEPRINTS:
    print(' * Registering blueprint "%s"' % blueprint.name)
    app.register_blueprint(blueprint)

# subdomain routes with special urls
app.register_blueprint(admin, url_prefix='/subdomain/<string:queue_url>/admin')
app.register_blueprint(queue, url_prefix='/subdomain/<string:queue_url>')

# register error handlers
app.register_error_handler(404, error_not_found)
app.register_error_handler(500, error_server)

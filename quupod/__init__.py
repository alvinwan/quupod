"""Quupod application factory."""

from .models import db
from .models import migrate
from .models import migration_manager
from .models import toolbar
from .views import login_manager
from .views import socketio
from .views import error_not_found
from .views import error_server
from .views import standard_error

from flask import Flask

import eventlet

CONFIG_PATH_FORMAT = '%s.config.%s'
LOG_FORMAT = ' * %s'
LOG_MODE_DEBUG = LOG_FORMAT % 'Running in DEBUG mode.'
LOG_MODE_PRODUCTION = LOG_FORMAT % 'Running in PRODUCTION mode.'
LOG_ID_FORMAT = LOG_FORMAT % 'Google Client ID: %s'
LOG_ID_NOT_FOUND = LOG_FORMAT % 'No Google Client ID found.'


def create_app(root: str, config: str) -> Flask:
    """Create a new Flask application with the provided configuration.

    :param root: The application root module name.
    :param config: The application configuration mode.
    """
    app = Flask(__name__)
    app.config.from_object(CONFIG_PATH_FORMAT % (root, config))

    if app.config['INIT']['debug']:
        print(LOG_MODE_DEBUG)
    else:
        print(LOG_MODE_PRODUCTION)

    if app.config['GOOGLECLIENTID']:
        print(LOG_ID_FORMAT % app.config['GOOGLECLIENTID'])
    else:
        print(LOG_ID_NOT_FOUND)

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
    app.register_blueprint(
        admin,
        url_prefix='/subdomain/<string:queue_url>/admin')
    app.register_blueprint(queue, url_prefix='/subdomain/<string:queue_url>')

    # register error handlers
    app.register_error_handler(401, standard_error)
    app.register_error_handler(404, error_not_found)
    app.register_error_handler(500, error_server)

    return app

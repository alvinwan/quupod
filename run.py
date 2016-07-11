"""Handle main application command-line interface.

Usage: run.py [--tornado]

Options:
  -h --help     Show this screen.
  --tornado     Run the application using tornado.
"""

from docopt import docopt
from flask import Flask
from quupod import create_app
from quupod import socketio
from quupod.models import db

import os

# Name of the application root module
ROOT = 'quupod'

# Two options: Development, Production
MODE = os.environ.get('MODE', 'Development')

# Define format for config mode
CONFIG_MODE_FORMAT = '%sConfig'


def main(app: Flask, tornado: bool=False) -> None:
    """Run the Flask application."""
    with app.app_context():
        db.create_all()
        print('[OK] Database creation complete.')

    if tornado:
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(int(app.config['INIT_PORT']))
        IOLoop.instance().start()
    else:
        socketio.run(app, **app.config['INIT'])


if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(
        create_app(ROOT, CONFIG_MODE_FORMAT % MODE),
        tornado=arguments['--tornado'])

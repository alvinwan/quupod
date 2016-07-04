"""Handle main application command-line interface.

Usage: run.py [--tornado]

Options:
  -h --help     Show this screen.
  --tornado     Run the application using tornado.
"""

from flask import Flask
from quupod import config
from quupod import app
from quupod import db
from quupod import socketio
from docopt import docopt


def run(app: Flask, tornado: bool=False) -> None:
    """Run the Flask application."""
    db.create_all()
    print('[OK] Database creation complete.')

    if tornado:
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop

        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(int(config['app_port']))
        IOLoop.instance().start()
    else:
        socketio.run(
            app,
            host='0.0.0.0',
            port=int(config['app_port']),
            debug=config['debug'])

if __name__ == "__main__":
    arguments = docopt(__doc__)
    run(app, tornado=arguments['--tornado'])

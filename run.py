from quuupod import app, debug, db
from quuupod.models import Setting
import argparse
import os


def run(app, with_tornado=False):
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    # create database
    db.create_all()
    print('[OK] Database creation complete.')

    # get application port
    port = int(os.environ.get('PORT', 5000))

    if with_tornado:
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(port)
        IOLoop.instance().start()
    else:
        app.run(host='0.0.0.0', port=port, debug=debug)


parser = argparse.ArgumentParser(description='Small manager for this queue application.')
parser.add_argument('-d', '--database', type=str,
                   help='Database operation',
                   choices=('default', 'override'))
parser.add_argument('-t', '--tornado', action='store_const', const=True,
                    default=False, help='launch with tornado')

if __name__ == "__main__":
    args = parser.parse_args()
    if args.database == 'create':
        db.create_all()
        print('[OK] Database creation complete.')
        print("""---

[OK] Database creation complete.
Use 'make run' to launch server.
    """)
    elif args.tornado:
        run(app, with_tornado=True)
    else:
        run(app)

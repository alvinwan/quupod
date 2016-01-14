from queue import app, debug
from dbcreate import dbcreate

if __name__ == "__main__":
    dbcreate()
    app.run(debug=debug)

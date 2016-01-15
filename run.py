from queue import app, debug
from dbcreate import dbcreate
from default_settings import load_settings
import os

if __name__ == "__main__":
    dbcreate()
    load_settings()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)

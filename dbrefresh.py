from queue import db
from dbcreate import dbcreate
from default_settings import load_settings

def dbrefresh():
    """Refresh database"""
    db.drop_all()
    dbcreate()

if __name__ == '__main__':
    dbrefresh()

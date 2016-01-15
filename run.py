from queue import app, debug, db
from queue.models import Setting, add_obj
import argparse
import os


def db_refresh():
    """Refresh database"""
    db.drop_all()
    dbcreate()


def db_create():
    """Create database"""
    db.create_all()
    load_settings()


def load_settings(override=False):
    """Add default settings to database if settings do not already exist."""
    for setting in default_settings:
        if not Setting.query.filter_by(name=setting['name']).first() or override:
            add_obj(Setting(**setting))


def run(app):
    db_create()
    print('[OK] Database creation complete.')
    load_settings()
    print('[OK] Default settings added.')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)


default_settings = [
    {
        'name': 'Name',
        'description': 'Name of your queue application',
        'value': 'CS70',
        'toggable': False
    }, {
        'name': 'Description',
        'description': 'byline displayed on the front page',
        'value': 'Discrete Mathematics and Probability Theory',
        'toggable': False
    }, {
        'name': 'URL',
        'description': 'course website URL',
        'value': 'cs70berkeley.com',
        'toggable': False
    }, {
        'name': 'Large Banner',
        'description': 'Display a large banner with basic course details and possibly announcements.',
        'enabled': False,
        'enable_description': 'Enable to include a section at the top of the queue, for announcements.',
        'toggable': True,
        'input_type': 'None'
    }, {
        'name': 'Google Login',
        'description': 'Allow users to login using Google.',
        'enabled': True,
        'toggable': True,
        'input_type': 'None'
    }, {
        'name': 'Default Login',
        'description': 'Allow users to register and login with the built-in system.',
        'enabled': False,
        'toggable': True,
        'input_type': 'None'
    }, {
        'name': 'Require Login',
        'description': 'Require login to place inquiries, or allow anonymous users to create inquiries.',
        'enabled': False,
        'enable_description': 'Enable to forbid unregistered users from submitting inquiries.',
        'toggable': True,
        'input_type': 'None'
    }, {
        'name': 'Inquiry Types',
        'description': 'Comma-separated list of all inquiry types',
        'enabled': False,
        'enable_description': 'Enable to specify different inquiry types. These types can then have restrictions applied.',
        'value': 'question',
        'toggable': True
    }, {
        'name': 'Assignments',
        'description': 'Comma-separated list of active assignments e.g., <code>hw0,hw1,proj2</code>. To specify different active assignments for each inquiry type, put each inquiry type on a new line, and prefix the list of assignments with <code>[inquiry type]:</code>. For inquiry types that should not have any assignment restrictions, simply leave the inquiry type out, or use <code>*</code>',
        'enabled': False,
        'enable_description': 'Enable to restrict assignments students may place inquiries for.',
        'value': 'hw0,hw1',
        'toggable': True,
        'input_type': 'textarea'
    }, {
        'name': 'Location Selection',
        'description': 'Toggle whether or not inquiries will contain location information.',
        'enabled': True,
        'enable_description': 'Enable to give users the option to specify a location for an inquiry.',
        'toggable': True,
        'input_type': 'None'
    }, {
        'name': 'Locations',
        'description': 'Manually specify a comma-separated list of locations. Only takes effect if "Location Selection" is enabled',
        'enabled': True,
        'enable_description': 'Enable to manually specify a list of locations.',
        'value': 'Evans B4',
        'toggable': False
    }
]


parser = argparse.ArgumentParser(description='Small manager for this queue application.')
parser.add_argument('-s', '--settings', type=str,
                   help='Whether or not to override default settings',
                   choices=('default', 'override'))
parser.add_argument('-db', '--database', type=str,
                   help='The database script to run',
                   choices=('create', 'refresh'))


if __name__ == "__main__":
    args = parser.parse_args()
    if args.database == 'create':
        db_create()
        print("""---

[OK] Database creation complete.
Use 'make run' to launch server.
    """)
    elif args.database == 'refresh':
        db_refresh()
        print("""---

[OK] Database refresh complete.
Use 'make run' to launch server.
    """)
    elif args.settings == 'default':
        load_settings()
        print("""---

[OK] Default settings loaded.
Use 'make run' to launch server.
    """)
    elif args.settings == 'override':
            load_settings(override=True)
            print("""---

    [OK] Default settings loaded.
    Use 'make run' to launch server.
        """)
    else:
        run(app)

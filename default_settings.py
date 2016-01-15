from queue.models import Setting, add_obj

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

def load_settings():
    """Add default settings to database if settings do not already exist."""
    for setting in default_settings:
        if not Setting.query.filter_by(name=setting['name']).first():
            add_obj(Setting(**setting))

if __name__ == '__main__':
    load_settings()
    print("""---

    [OK] Default settings loaded.
    Use 'make run' to launch server.
    """)


default_queue_settings = {
    'large_banner': {
        'label': 'Large Banner',
        'description': 'Display a large banner with basic course details and possibly announcements.',
        'enabled': False,
        'enable_description': 'Enable to include a section at the top of the queue, for announcements.',
        'toggable': True,
        'input_type': 'None'
    },
    'require_login': {
        'label': 'Require Login',
        'description': 'Require login to place inquiries, or allow anonymous users to create inquiries.',
        'enabled': False,
        'enable_description': 'Enable to forbid unregistered users from submitting inquiries.',
        'toggable': True,
        'input_type': 'None'
    },
    'inquiry_types': {
        'label': 'Inquiry Types',
        'description': 'Comma-separated list of all inquiry types',
        'enabled': False,
        'enable_description': 'Enable to specify different inquiry types. These types can then have restrictions applied.',
        'value': 'question',
        'toggable': True
    },
    'assignments': {
        'label': 'Assignments',
        'description': 'Comma-separated list of active assignments e.g., <code>hw0,hw1,proj2</code>. To specify different active assignments for each inquiry type, put each inquiry type on a new line, and prefix the list of assignments with <code>[inquiry type]:</code>. For inquiry types that should not have any assignment restrictions, simply leave the inquiry type out, or use <code>*</code>',
        'enabled': False,
        'enable_description': 'Enable to restrict assignments students may place inquiries for.',
        'value': 'hw0,hw1',
        'toggable': True,
        'input_type': 'textarea'
    },
    'location_selection': {
        'label': 'Location Selection',
        'description': 'Toggle whether or not inquiries will contain location information.',
        'enabled': True,
        'enable_description': 'Enable to give users the option to specify a location for an inquiry.',
        'toggable': True,
        'input_type': 'None'
    },
    'locations': {
        'label': 'Locations',
        'description': 'Manually specify a comma-separated list of locations. Only takes effect if "Location Selection" is enabled',
        'enabled': True,
        'enable_description': 'Enable to manually specify a list of locations.',
        'value': 'Evans B4',
        'toggable': False
    },
    'whitelist': {
        'label': 'Admin Whitelist',
        'description': 'Whitelist for admins',
        'enabled': True,
        'toggable': False
    }
}

default_queue_roles = {
    'class': [
        {
            'name': 'Owner',
            'permissions': '*'
        },
        {
            'name': 'Admin',
            'permissions': '*'
        },
        {
            'name': 'Staff',
            'permissions': 'help',
        },
        {
            'name': 'Member',
            'permissions': ''
        }
    ],
    'nonprofit': [
        {
            'name': 'Owner',
            'permissions': '*'
        },
        {
            'name': 'Admin',
            'permissions': '*'
        },
        {
            'name': 'Lead',
            'permissions': 'help'
        },
        {
            'name': 'Member',
            'permissions': ''
        }
    ]
}

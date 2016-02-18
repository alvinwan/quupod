
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
        'description': 'Manually specify a comma-separated list of locations. Only takes effect if "Location Selection" is enabled. <b>No spaces!</b> All spaces will be removed upon save.',
        'enabled': True,
        'enable_description': 'Enable to manually specify a list of locations.',
        'value': 'EvansB4',
        'toggable': False
    },
    'whitelist': {
        'label': 'Admin Whitelist',
        'description': 'Whitelist for admins. Include users as email1@berkeley.edu(Position1), email2@berkeley.edu(Position2)',
        'enabled': True,
        'toggable': False
    },
    'max_requests': {
        'label': 'Maximum Concurrent Requests',
        'description': 'Maximum number of times users can place a request on the queue, concurrently',
        'value': '1',
        'enabled': True,
        'toggable': True
    },
    'self_promotion': {
        'label': 'Self-promoting via URL',
        'description': 'Allow users to promote themselves to admin or staff via <code>/promote</code>. Optionally, specify codewords below for each position. Use the asterisk <code>*</code> to denote "no codeword required". Any role not included below does not allow self-promotion. Each line should contain <code>[role]:[password]</code>. Put each role on a new line.',
        'enabled': True,
        'enable_description': 'Enable to allow staff members to promote themselves to staff.',
        'value': 'role1:codeword1\nrole2:codeword2',
        'toggable': True,
        'input_type': 'textarea'
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

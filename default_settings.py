default_settings = [
    {
        'name': 'Name',
        'description': 'Name of your queue application',
        'value': 'CS70',
        'toggable': False
    }, {
        'name': 'Inquiry Types',
        'description': 'Comma-separated list of all inquiry types',
        'enabled': False,
        'enable_description': 'Enable to specify different inquiry types. These types can then be prioritized in the queue or have different restrictions applied.',
        'value': 'question'
        'toggable': True
    }, {
        'name': 'Assignments',
        'description': 'Comma-separated list of active assignments e.g., <code>hw0,hw1,proj2</code>. To specify different active assignments for each inquiry type, put each inquiry type on a new line, and prefix the list of assignments with <code>\<inquiry type\>:</code>',
        'enabled': False,
        'enable_description': 'Enable to restrict assignments students may place inquiries for.',
        'value': 'hw0,hw1',
        'toggable': True
    }, {
        'name': 'Processing Priority',
        'description': 'Comma-separated list of priorities. The order of priorities listed here will determine the order in which inquiries are processed.',
        'enabled': False,
        'enable_description': 'Enable to specify priority by inquiry type. Default is to order all inquiries, regardless of type, by time.',
        'toggable': True
    }
]

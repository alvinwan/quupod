"""All notifications."""

ERR_NO_LOGIN = 0
NOTIF_LOGIN_STAFF = 1
NOTIF_LOGIN_STUDENT = 2
NOTIF_SETTING_UPDATED = 3
NOTIF_SETTING_ONE_TYPE = 4
NOTIF_INQUIRY_PLACED = 5
NOTIF_HELP_DONE = 6

notifications = {
    ERR_NO_LOGIN: 'You are attempting to <b>disable both login methods</b> - '
    'Google login and Default login. To change from one login method to the '
    'other, enable both first, then disable one! Settings unchanged.',
    NOTIF_LOGIN_STAFF: 'Hello there! <b>Click on "start helping" in the '
    'bottom-right corner</b> to start helping.',
    NOTIF_LOGIN_STUDENT: 'Hello there! Click on <b>"request help" in the '
    'bottom-right corner</b> to enqueue yourself.',
    NOTIF_SETTING_UPDATED: 'Settings have been updated.',
    NOTIF_SETTING_ONE_TYPE: 'You have "Inquiry Types" enabled, but there is'
    ' only one type for students to choose from! Recommended: update the '
    '"Inquiry Types" field below with a comma-separated list of values, or '
    'disable it.',
    NOTIF_INQUIRY_PLACED: 'Your request has been placed! A staff member will '
    'be in touch soon.',
    NOTIF_HELP_DONE: 'All inquiries for your location are processed!'
}

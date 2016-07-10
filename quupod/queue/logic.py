"""Logic for all non-admin queue views."""

from flask import g
from quupod.defaults import default_queue_settings
from quupod.models import Inquiry
from quupod.views import current_user


def get_inquiry_for_asker(inquiry_id: int) -> Inquiry:
    """Fetch the current inquiry for the asker."""
    if inquiry_id:
        return Inquiry.query.get(inquiry_id)
    else:
        return Inquiry.get_current_asking()


def maybe_promote_current_user():
    """Whitelist the current user if the user is on the whitelist."""
    whitelist = g.queue.setting('whitelist').value
    if whitelist:
        entries = {}
        for entry in whitelist.split(','):
            entry = tuple(s.strip() for s in entry.split('('))
            if len(entry) == 2:
                entries[entry[0]] = entry[1][:-1]
            else:
                entries[entry[0]] = 'Staff'
        if current_user().is_authenticated and \
                current_user().email in entries:
            current_user().set_role(entries[current_user().email])


def update_context_with_queue_config(context):
    """Update the template environment with queue configuration."""
    for k in default_queue_settings:
        setting = g.queue.setting(k)
        context.update({
            'queue_setting_%s' % k: setting.value or setting.enabled})

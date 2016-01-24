from functools import wraps
from flask import url_for, redirect, render_template, request
import flask_login
from quuupod.notifications import *
from quuupod import googleclientID
from quuupod.public.controllers import get_user_home
from quuupod.admin.controllers import setting, get_setting
from run import default_settings


def render(template, **kwargs):
    """Render with settings"""
    for k in (s['name'] for s in default_settings):
        is_enabled = get_setting(name=k).enabled
        if is_enabled:
            value = setting(k) or is_enabled
        else:
            value = False
        kwargs.setdefault('app_%s' % k.lower().replace(' ', '_'), value)
    return render_template(template,
        googleclientID=googleclientID,
        banner_message=notifications.get(
            int(request.args.get('notification', None) or -1), None),
        **kwargs)


def anonymous_required(f):
    """Decorator for views that require anonymous users (e.g., sign in)"""
    @wraps(f)
    def decorator(*args, **kwargs):
        user = flask_login.current_user
        if user.is_authenticated:
            return get_user_home(user)
        return f(*args, **kwargs)
    return decorator


def requires(*roles):
    """Decorator for views, restricting access to the roles listed"""
    def wrap(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if getattr(flask_login.current_user, 'role', None) not in roles:
                return 'Permission denied.'
            return f(*args, **kwargs)
        return decorator
    return wrap

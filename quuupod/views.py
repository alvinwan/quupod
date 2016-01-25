from functools import wraps
from flask import url_for, redirect, render_template, request
import flask_login
from quuupod.defaults import default_queue_settings
from quuupod.notifications import *
from quuupod import googleclientID, config
from flask_login import login_required


def current_user():
    """Returns currently-logged-in user"""
    return flask_login.current_user


def render(template, **kwargs):
    """Render with settings"""
    for k, v in config.items():
        kwargs.setdefault('cfg_%s' % k, v)
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

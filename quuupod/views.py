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
    kwargs.setdefault('request', request)
    kwargs.setdefault('logout', request.args.get('logout', False))
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
            return User.get_home(user)
        return f(*args, **kwargs)
    return decorator


def requires(*permissions):
    """Decorator for views, restricting access to the roles listed"""
    from quuupod.queue.views import render_queue
    def wrap(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            user = flask_login.current_user
            if not all(user.can(perm) for perm in permissions):
                return render_queue('error.html',
                    message='Permission Denied.',
                    action='Home',
                    url=url_for('queue.home'))
            return f(*args, **kwargs)
        return decorator
    return wrap

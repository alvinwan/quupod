from functools import wraps
from flask import url_for, redirect, render_template, request, g
import flask_login
from quupod.defaults import default_queue_settings
from quupod.notifications import *
from quupod import googleclientID, config, debug, domain
from flask_login import login_required


def current_user():
    """Returns currently-logged-in user"""
    return flask_login.current_user


def render(template, **kwargs):
    """Render with settings"""
    for k, v in config.items():
        kwargs.setdefault('cfg_%s' % k, v)
    if not debug: # if on production
        kwargs.setdefault('domain', domain)
    return render_template(template,
        googleclientID=googleclientID,
        banner_message=notifications.get(
            int(request.args.get('notification', None) or -1), None),
        request=request,
        logout=request.args.get('logout', False),
        the_url=the_url,
        current_url=current_url,
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
    from quupod.queue.views import render_queue
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


def strip_subdomain(string, n=1):
    """Strip subdomain prefix if applicable"""
    if '/subdomain/' not in request.path:
        return string
    return '/' + '/'.join([s for s in string.split('/') if s][n:])


def current_url():
    """Return current URL"""
    return strip_subdomain(request.path, n=2)


def the_url(*args, **kwargs):
    """Special url function for subdomain websites"""
    return strip_subdomain(url_for(*args, **kwargs))

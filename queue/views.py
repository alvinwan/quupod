from functools import wraps
from flask import url_for, redirect, render_template, request
import flask_login
from queue.errors import *
from queue import googleclientID
from queue.public.controllers import get_user_home
from queue.admin.controllers import setting, get_setting
from default_settings import default_settings


def render(template, **kwargs):
    """Render with settings"""
    for k in (s['name'] for s in default_settings):
        value = setting(k) or get_setting(name=k).enabled
        kwargs.setdefault('app_%s' % k.lower().replace(' ', '_'), value)
    return render_template(template,
        googleclientID=googleclientID,
        banner_message=error_messages.get(
            int(request.args.get('error', None) or -1), None),
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

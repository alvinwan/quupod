from functools import wraps
from flask import url_for, redirect, render_template
import flask_login
from queue import googleclientID
from queue.public.controllers import get_user_home
from queue.admin.controllers import setting
from default_settings import default_settings


def render(template, **kwargs):
    """Render with settings"""
    for k in (s['name'] for s in default_settings):
        kwargs.setdefault('app_%s' % k.lower(), setting(k))
    return render_template(template, googleclientID=googleclientID, **kwargs)


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

from functools import wraps
from flask import url_for, redirect
import flask_login


def anonymous_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        user = flask_login.current_user
        if get_user_home(user):
            return get_user_home(user)
        return f(*args, **kwargs)
    return decorator

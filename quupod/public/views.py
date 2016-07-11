"""Handle all public pages."""

from .logic import get_google_auth_flow
from .logic import get_google_authorize_uri
from .logic import get_google_person

from flask import Blueprint
from flask import request
from flask import redirect
from oauth2client import client
from quupod.models import User
from quupod.models import Queue
from quupod.views import render
from quupod.views import url_for
from quupod.views import login_manager
from werkzeug.local import LocalProxy

import flask_login

public = Blueprint('public', __name__, template_folder='templates')

#########
# QUEUE #
#########


@public.route('/')
def home() -> str:
    """List of all 'unresolved' inquiries for the homepage."""
    return render('public/index.html', queues=Queue.query.all())

###################
# SIGN IN/SIGN UP #
###################


@public.route('/login', methods=['POST', 'GET'])
def login(home: str=None, login: str=None) -> str:
    """Login using Google authentication.

    :param home: URL for queue homepage
    :param login: URL for queue login page
    """
    try:
        flow = get_google_auth_flow(login)
        if 'code' not in request.args:
            return redirect(get_google_authorize_uri(flow))
        person = get_google_person(flow)
        user = User.query.filter_by(google_id=person['id']).first()
        if not user:
            user = User(
                name=person['displayName'],
                email=person['emails'][0]['value'],
                google_id=person['id'],
                image_url=person['image']['url']).save()
        flask_login.login_user(user)
        return redirect(home or url_for('public.home'))
    except client.FlowExchangeError:
        return redirect(login or url_for('public.login'))


######################
# SESSION UTILIITIES #
######################

@login_manager.user_loader
def user_loader(id: int) -> str:
    """Load user from a given integer id."""
    return User.query.get(id)


@login_manager.request_loader
def request_loader(request: LocalProxy) -> str:
    """Load user from Flask Request object."""
    user = User.query.get(int(request.form.get('id') or 0))
    if not user:
        return
    user.is_authenticated = user.password == request.form['password']
    return user


@public.route('/logout')
def logout(home: str=None) -> str:
    """Log out current session and redirect to home.

    :param home: URL to redirect to after logout success
    """
    flask_login.logout_user()
    return redirect(
        request.args.get(
            'redirect',
            home or url_for('public.home')))


@login_manager.unauthorized_handler
def unauthorized_handler():
    """Redirect unauthorized users to the public queue home page."""
    return redirect(url_for('public.home'))

from flask import Blueprint, request, render_template, url_for, redirect
from .forms import *
from quupod import app, login_manager, whitelist, googleclientID
from quupod.models import User, Inquiry, Queue
from quupod.views import anonymous_required, render
from quupod.notifications import *
from oauth2client import client, crypt
import flask_login

public = Blueprint('public', __name__, template_folder='templates')

#########
# QUEUE #
#########

@public.route('/')
def home():
    """List of all 'unresolved' inquiries for the homepage"""
    return render('index.html', queues=Queue.query.all())

###################
# SIGN IN/SIGN UP #
###################


@public.route('/tokenlogin', methods=['POST'])
@public.route('/<path:random>/tokenlogin', methods=['POST'])
@anonymous_required
def token_login():
    """Login via Google token"""
    redirect = request.form.get('return', None)
    if flask_login.current_user.is_authenticated:
        return redirect or url_for('dashboard.home')
    google_info = verify_google_token(request.form['token'])

    if google_info:
        print(' * Google Token verified!')
        google_id = google_info['sub']
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            print(' * Registering user using Google token...')
            user = User(
                name=google_info['name'],
                email=google_info['email'],
                google_id=google_id
            ).save()
        flask_login.login_user(user)
        # if user and user.can('help'):
        #     path, notification = 'admin.home', NOTIF_LOGIN_STAFF
        # else:
            # path, notification = 'public.home', NOTIF_LOGIN_STUDENT
        path, notification = 'dashboard.home', NOTIF_LOGIN_STUDENT
        if redirect:
            return redirect + '?notification=%s' % notification
        return url_for(path, notification=notification)
    return 'Google token verification failed.'


def verify_google_token(token):
    """
    Verify a google token

    :param token str: token
    :return: token information if valid or None
    """
    try:
        idinfo = client.verify_id_token(token, googleclientID)
        #If multiple clients access the backend server:
        if idinfo['aud'] not in [googleclientID]:
            raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
        # Is this needed?
        # if idinfo['hd'] != url_for('public.home'):
        #     raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        return
    return idinfo


######################
# SESSION UTILIITIES #
######################

@login_manager.user_loader
def user_loader(id):
    """Load user by id"""
    print(' * Reloading user with id "%s", from user_loader' % id)
    return User.query.get(id)

@login_manager.request_loader
def request_loader(request):
    """Loads user by Flask Request object"""
    id = int(request.form.get('id') or 0)
    user = User.query.get(id)
    if not user:
        print(' * Anonymous user found.')
        return
    # encryption handled by SQLAlchemy PasswordType field
    user.is_authenticated = user.password == request.form['password']
    if user.is_authenticated:
        print(' * Reloaded user with id "%s", from request_loader' % id)
    return user

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(request.args.get('redirect',
        url_for('public.home')) + '?logout=true')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('public.home'))

##################
# ERROR HANDLERS #
##################

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html',
        title='404. Oops.',
        code=404,
        message='Oops. This page doesn\'t exist!',
        url=url_for('public.home'),
        action='Return to homepage?'), 404


@app.errorhandler(500)
def not_found(error):
    from quupod import db
    db.session.rollback()
    return render_template('500.html',
        title='500. Hurr.',
        code=500,
        message='Sorry, try again! Sometimes, our server goes to sleep, which causes our application to crash. If this problem persists, file an issue on the <a href="https://github.com/CS70/ohquu/issues">Github issues page</a>.',
        url=request.path,
        action='Reload'), 500

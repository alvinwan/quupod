from flask import Blueprint, request, render_template, redirect, session, abort
from .forms import *
from quupod import app, login_manager, whitelist, googleclientID
from quupod.models import User, Inquiry, Queue
from quupod.views import anonymous_required, render, url_for, current_url, current_user
from quupod.notifications import *
from oauth2client import client, crypt
import flask_login
from apiclient.discovery import build
from quupod.config import config
import httplib2

service = build('plus', 'v1')

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


@public.route('/login', methods=['POST', 'GET'])
def login():
    """Login"""
    try:
        flow = client.flow_from_clientsecrets(
            'client_secrets.json',
            scope='openid profile email',
            redirect_uri=url_for('public.login', _external=True))
        if 'code' not in request.args:
            auth_uri = flow.step1_get_authorize_url()
            return redirect(auth_uri+'&prompt=select_account')
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        google_info = credentials.id_token

        http = httplib2.Http()
        http = credentials.authorize(http)
        people_resource = service.people()
        people_document = people_resource.get(userId='me').execute(http=http)

        google_id = google_info['sub']
        print(' * Google Token verified!')
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            print(' * Registering user using Google token...')
            user = User(
                name=google_info['name'],
                email=google_info['email'],
                google_id=google_id
            ).save()
        flask_login.login_user(user)
        print('* %s logged in (%s)' % (user.name, user.email))
        return redirect(url_for('public.home'))
    except client.FlowExchangeError:
        return redirect(url_for('public.login'))


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
    return render('error.html',
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
        domain=config['DOMAIN'],
        title='500. Hurr.',
        code=500,
        message='Sorry. Here is the error: <br><code>%s</code><br> Please file an issue on the <a href="https://github.com/CS70/ohquu/issues">Github issues page</a>, with the above code if it has not already been submitted.' % str(error)), 500

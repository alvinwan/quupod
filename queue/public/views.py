from flask import Blueprint, request, render_template
from .forms import *
from .controllers import *
from queue import app, login_manager, whitelist
from queue.admin.controllers import setting
from queue.admin.models import User, Inquiry
from queue.views import anonymous_required, render
from queue.notifications import *
import flask_login

public = Blueprint('public', __name__, template_folder='templates')

#########
# QUEUE #
#########

@public.route('/')
def home():
    """List of all 'unresolved' inquiries for the homepage"""
    return render('queue.html',
        inquiries=unresolved_inquiries(),
        panel='Unresolved',
        empty='No unaddressed inquiries!',
        ttr=ttr(),
        logout=request.args.get('logout', 'false'))

@public.route('/resolving')
def resolving():
    """List of all 'resolving' inquiries for the homepage"""
    return render('resolving.html',
        inquiries=resolving_inquiries(),
        panel='Resolving',
        empty='No inquiries currently being resolved.',
        ttr=ttr())

@public.route('/staff')
def staff():
    """Lists all staff present at the current event."""
    return render('staff.html',
        staff=present_staff(),
        panel='Staff',
        empty='No staff members currently present.',
        ttr=ttr())

@public.route('/request', methods=['POST', 'GET'])
def inquiry():
    """
    Place a new request, which may be authored by either a system user or an
    anonymous user.
    """
    user, form = flask_login.current_user, InquiryForm(request.form)
    if user.is_authenticated:
        form = InquiryForm(request.form, obj=user)
    elif get_setting(name='Require Login').enabled:
        if get_setting(name='Google Login').enabled and not \
            get_setting(name='Default Login').enabled:
            return render('confirm.html',
                title='Login Required',
                message='Login via Google (in the top navigation bar) to add an inquiry.',
                action='Home',
                url=url_for('public.home'))
        return render('confirm.html',
            title='Login Required',
            message='Login to add an inquiry, and start using this queue.',
            action='Login',
            url=url_for('public.login'))
    form = add_inquiry_choices(form)
    if request.method == 'POST' and form.validate() and \
        valid_assignment(request, form):
        inquiry = add_inquiry(request.form)
        return redirect(url_for('public.home',
            notification=NOTIF_INQUIRY_PLACED))
    return render('form.html', form=form, title='Request Help',
        submit='Ask')

###################
# SIGN IN/SIGN UP #
###################

@public.route('/login', methods=['POST', 'GET'])
@anonymous_required
def login():
    """Login"""
    form, message = LoginForm(request.form), ''
    if not get_setting(name='Default Login').enabled:
        return render('confirm.html', title='Disabled',
            message='Default registration and login has been disabled. Authenticate using Google (in the top navigation bar).',
            action='Home',
            url=url_for('public.home'))
    if request.method == 'POST' and form.validate():
        user = get_user(username=request.form['username'])
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(get_user_url(user))
        message = 'Login failed.'
    return render('form.html', message=message, form=form,
        title='Login', submit='Login')

@public.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """Register"""
    form = RegisterForm(request.form)
    if not get_setting(name='Default Login').enabled:
        return render('confirm.html', title='Disabled',
            message='Default registration and login has been disabled. Authenticate using Google (in the top navigation bar).',
            action='Home',
            url=url_for('public.home'))
    if request.method == 'POST' and form.validate():
        return render('confirm.html', **add_user(request.form))
    return render('form.html', form=form, title='Register',
        submit='Register')

@public.route('/tokenlogin', methods=['POST'])
@anonymous_required
def token_login():
    """Login via Google token"""
    google_info = verify_google_token(request.form['token'])
    if google_info:
        print(' * Google Token verified!')
        google_id = google_info['sub']
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            print(' * Registering user using Google token...')
            user = add_obj(User(
                name=google_info['name'],
                email=google_info['email'],
                google_id=google_id
            ))
        login_user(user)
        if user and getattr(user, 'role', None) == 'staff':
            return url_for('admin.home', notification=NOTIF_LOGIN_STAFF)
        return url_for('public.home', notification=NOTIF_LOGIN_STUDENT)
    return 'Google token verification failed.'

######################
# SESSION UTILIITIES #
######################

@login_manager.user_loader
def user_loader(id):
    """Load user by id"""
    print(' * Reloading user with id "%s", from user_loader' % id)
    return get_user(id=id)

@login_manager.request_loader
def request_loader(request):
    """Loads user by Flask Request object"""
    id = request.form.get('id')
    user = get_user(id=id)
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
    return redirect(url_for('public.home', logout='true'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return get_user_home(flask_login.current_user)

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
    from queue import db
    db.session.rollback()
    return render_template('500.html',
        title='500. Hurr.',
        code=500,
        message='Sorry, try again! Sometimes, our server goes to sleep, which causes our application to crash. If this problem persists, file an issue on the <a href="https://github.com/CS70/ohquu/issues">Github issues page</a>.',
        url=request.path,
        action='Reload'), 500

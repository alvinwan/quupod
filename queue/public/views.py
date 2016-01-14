from flask import Blueprint, request
from .forms import *
from .controllers import *
from queue import app, login_manager, whitelist
from queue.admin.controllers import setting
from queue.admin.models import User, Inquiry
from queue.views import anonymous_required, render
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
        ttr=ttr())

@public.route('/resolving')
def resolving():
    """List of all 'resolving' inquiries for the homepage"""
    return render('queue.html',
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

@public.route('/inquiry', methods=['POST', 'GET'])
def inquiry():
    """
    Place a new inquiry, which may be authored by either a system user or an
    anonymous user.
    """
    user, form = flask_login.current_user, InquiryForm(request.form)
    if user.is_authenticated:
        form = InquiryForm(request.form, obj=user)
    form = add_inquiry_choices(form)
    if request.method == 'POST' and form.validate() and \
        valid_assignment(request, form):
        return render('confirm.html', **add_inquiry(request.form))
    print(form.errors)
    return render('form.html', form=form, title='Add Inquiry',
        submit='Ask')

###################
# SIGN IN/SIGN UP #
###################

@public.route('/login', methods=['POST', 'GET'])
@anonymous_required
def login():
    """Login"""
    form, message = LoginForm(request.form), ''
    if request.method == 'POST' and form.validate():
        user = get_user(username=request.form['username'])
        if user and user.password == request.form['password']:
            return redirect(login_and_url(user))
        message = 'Login failed.'
    return render('form.html', message=message, form=form,
        title='Login', submit='Login')

@public.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """Register"""
    form = RegisterForm(request.form)
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
        return login_and_url(user)
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
    return redirect(url_for('public.home'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return get_user_home(flask_login.current_user)

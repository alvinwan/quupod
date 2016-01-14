from flask import Blueprint, request
from .forms import *
from .controllers import *
from queue import app, login_manager, whitelist
from queue.admin.models import User, Inquiry
from queue.views import anonymous_required, render
import flask_login

public = Blueprint('public', __name__, template_folder='templates')

#########
# QUEUE #
#########

@public.route('/')
def home():
    """List of all 'unresolved' and 'resolving' inquiries for the homepage"""
    return render('queue.html',
        unresolved=unresolved_inquiries(),
        resolving=resolving_inquiries())

@public.route('/inquiry', methods=['POST', 'GET'])
def inquiry():
    """
    Place a new inquiry, which may be authored by either a system user or an
    anonymous user.
    """
    user, form = flask_login.current_user, InquiryForm(request.form)
    if user.is_authenticated:
        form = InquiryForm(request.form, obj=user)
    form.category.choices = [(s, s) for s in ('question', 'tutoring')]
    if request.method == 'POST' and form.validate():
        return render('confirm.html', **add_inquiry(request.form))
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
            flask_login.login_user(user)
            whitelist_promote(user)
            print(' * %s (%s) logged in.' % (user.name, user.email))
            return get_user_home(user)
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

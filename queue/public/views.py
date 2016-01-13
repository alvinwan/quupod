from flask import Blueprint, render_template, request
from .forms import *
from .controllers import *
from queue import app, login_manager
from queue.staff.models import User, Inquiry
from queue.views import anonymous_required
import flask_login

public = Blueprint('public', __name__)

#########
# QUEUE #
#########

@public.route('/')
def home():
    """List of all 'unresolved' and 'resolving' inquiries for the homepage"""
    return render_template('queue.html',
        unresolved=unresolved_inquiries(),
        resolving=resolving_inquiries())

@public.route('/inquiry', methods=['POST', 'GET'])
def inquiry():
    """
    Place a new inquiry, which may be authored by either a system user or an
    anonymous user.
    """
    form, user = InquiryForm(request.form), flask_login.current_user
    if request.method == 'POST' and form.validate():
        if user.is_authenticated:
            data = multi2dict(request.form)
            data.update({'name': user.name})
        else:
            data = request.form
        return render_template('confirm.html', **add_inquiry(data))
    return render_template('inquiry.html', form=form)

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
            print(' * %s (%s) logged in.' % (user.name, user.email))
            return get_user_home(user)
        message = 'Login failed.'
    return render_template('login.html', message=message, form=form)

@public.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """Register"""
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('confirm.html', **add_user(request.form))
    return render_template('register.html', form=form)

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

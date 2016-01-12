from flask import Blueprint, render_template, request
from .forms import *
from .controllers import *
from queue import app
from queue.staff.models import User, Inquiry

public = Blueprint('public', __name__)

#########
# QUEUE #
#########

@app.route('/')
def queue():
    """List of all 'unresolved' inquiries for the homepage"""
    return render_template('queue.html',
        inquiries=queued_inquiries(request.form))

@app.route('/inquiry', methods=['POST', 'GET'])
def inquiry():
    """
    Place a new inquiry, which may be authored by either a system user or an
    anonymous user.
    """
    form = InquiryForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('confirm.html', **add_inquiry(request.form))
    return render_template('inquiry.html', form=form)

###################
# SIGN IN/SIGN UP #
###################

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    """Sign in"""
    form = SigninForm(request.form)
    if request.method == 'POST' and form.validate():
        pass  # sign in user
    return render_template('signin.html')

@app.route('/signup')
def signup():
    """Sign up"""
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        return render_template('confirm.html', **add_user(request.form))
    return render_template('signup.html')

######################
# SESSION UTILIITIES #
######################

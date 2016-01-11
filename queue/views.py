"""
Views for Queue

@author: Alvin Wan, Ben Kha
"""

from . import app
from .models import User, Request


#########
# QUEUE #
#########

@app.route('/')
def queue():
    """list of all requests"""
    requests = Request.query.filter_by(status='unresolved').all()
    return render_template('queue.html', requests=requests)


@app.route('/request', methods=['POST', 'GET'])
def request():
    """place a request"""
    if request.method == 'POST':
        
        pass  # save request in db
    return render_template('request.html')


@app.route('/help/<string:id>', methods=['POST', 'GET'])
def help(id):
    """automatically selects next request"""
    if request.method == 'POST':
        pass  # mark request as resolved
    # mark request as currently-being-resolved
    request = None
    return render_template('help.html', request=request)


###################
# SIGN IN/SIGN UP #
###################

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    """sign in"""
    if request.method == 'POST':
        pass  # sign in user
    return render_template('signin.html')


@app.route('/signup')
def signup():
    """sign up"""
    if request.method == 'POST':
        pass  # sign up user
    return render_template('signup.html')


#############
# ANALYTICS #
#############

@app.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')


#########
# ADMIN #
#########

@app.route('/admin')
def admin():
    """admin homepage"""
    # option to see analytics or to start helping
    return render_template('admin.html')

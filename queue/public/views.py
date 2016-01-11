"""
Public Views for Queue

@author: Alvin Wan, Ben Kha
"""

from flask import Blueprint, render_template, request
from queue import app
from queue.staff.models import User, Request

public = Blueprint('public', __name__)

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

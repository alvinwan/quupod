"""
Admin Views for Queue

@author: Alvin Wan, Ben Kha
"""

from flask import Blueprint, render_template, request
from queue import app
from .models import User, Request

staff = Blueprint('staff', __name__, url_prefix='/staff')

#########
# ADMIN #
#########

@app.route('/')
def home():
    """admin homepage"""
    # option to see analytics or to start helping
    return render_template('admin.html')

@app.route('/help/<string:id>', methods=['POST', 'GET'])
def help(id):
    """automatically selects next request"""
    if request.method == 'POST':
        pass  # mark request as resolved
    # mark request as currently-being-resolved
    request = None
    return render_template('help.html', request=request)

#############
# ANALYTICS #
#############

@app.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')

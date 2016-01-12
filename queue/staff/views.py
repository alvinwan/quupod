from flask import Blueprint, render_template, request
from queue import app
from .models import User, Inquiry
from .controllers import *


staff = Blueprint('staff', __name__, url_prefix='/staff')

#########
# ADMIN #
#########

@staff.route('/')
def home():
    """staff homepage"""
    # option to see analytics or to start helping
    return render_template('staff.html')

@staff.route('/help/<string:id>', methods=['POST', 'GET'])
@staff.route('/help')
def help(id=None):
    """automatically selects next inquiry"""
    inquiry = lock_inquiry(get_latest_inquiry(id))
    if request.method == 'POST':
        pass  # mark request as resolved
    return render_template('help.html', inquiry=inquiry)

#############
# ANALYTICS #
#############

@staff.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')

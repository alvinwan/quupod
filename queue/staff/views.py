from flask import Blueprint, render_template, request
from queue import app
from .models import User, Inquiry

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
    """automatically selects next inquiry"""
    inquiry = Inquiry.query.filter_by(id=id).first()
    if request.method == 'POST':
        pass  # mark request as resolved
    return render_template('help.html',inquiry=help_inquiry(inquiry), form=form)

#############
# ANALYTICS #
#############

@app.route('/analytics')
def analytics():
    """analytics for requests"""
    return render_template('analytics.html')

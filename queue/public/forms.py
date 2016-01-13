from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from wtforms.validators import InputRequired, DataRequired
import wtforms as wtf
from queue.admin.models import Inquiry, User
import flask_login


class LoginForm(wtf.Form):
    username = wtf.StringField()
    password = wtf.PasswordField()


class RegisterForm(ModelForm):
    """form for user register and login"""
    class Meta:
        model = User
        only = ('name', 'email', 'username', 'password')


class InquiryForm(ModelForm):
    """form for placing inquiries"""

    name = wtf.StringField('Name',
        description='your full name', validators=[DataRequired()])
    category = wtf.SelectField('Category',
        description='What type of inquiry are you submitting?', coerce=str)
    assignment = wtf.StringField('Assignment',
        description='<b>Use the following abbreviations</b>: <code>hw</code> for "homework", <code>proj</code> for "project", and <code>dis</code> for "discussion".', validators=[InputRequired()])
    problem = wtf.StringField('Problem',
        description='Be specific about which part, and do not include spaces or punctuation. For example, to specify problem 1 part a, only use <code>1a</code>.', validators=[InputRequired()])

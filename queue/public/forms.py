from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from wtforms.validators import InputRequired, DataRequired, Optional
import wtforms as wtf
from queue.admin.models import Inquiry, User
from queue.admin.controllers import setting, get_setting
import flask_login


class LoginForm(wtf.Form):
    username = wtf.StringField()
    password = wtf.PasswordField()


class RegisterForm(ModelForm):
    """form for user register and login"""
    class Meta:
        model = User
        only = ('name', 'email', 'username', 'password')


assignment_description = '<b>Use the following abbreviations</b>: <code>hw</code> for "homework", <code>proj</code> for "project", and <code>dis</code> for "discussion".'


class InquiryForm(ModelForm):
    """form for placing inquiries"""

    name = wtf.StringField('Name',
        description='Your full name', validators=[DataRequired()])
    category = wtf.SelectField('Category',
        description='What type of inquiry are you submitting?', coerce=str)
    location = wtf.SelectField('Location',
        description='Help us find you!', coerce=str, validators=[Optional()])
    assignment = wtf.StringField('Assignment',
        description=assignment_description, validators=[InputRequired()])
    problem = wtf.StringField('Problem',
        description='Be specific about which part, and do not include spaces or punctuation. For example, to specify problem 1 part a, only use <code>1a</code>.', validators=[Optional()])

    def __iter__(self):
        fields = []
        for k, v in self._fields.items():
            if (k == 'location' and not get_setting(name='Locations').enabled)\
                or (k == 'category' and not get_setting(
                    name='Inquiry Types').enabled):
                continue
            else:
                fields.append(v)
        return iter(fields)

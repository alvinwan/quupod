from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from flask import g
import wtforms as wtf
from quupod.models import Inquiry, User
import flask_login


class LoginForm(wtf.Form):
    username = wtf.StringField()
    password = wtf.PasswordField()


class RegisterForm(ModelForm):
    """form for user register and login"""
    class Meta:
        model = User
        only = ('name', 'email', 'username', 'password')

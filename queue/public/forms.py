from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
import wtforms as wtf
from queue.staff.models import Inquiry, User
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
    class Meta:
        model = Inquiry
        only = ('name', 'question')

    # assignment = 
    # problem =

    def __iter__(self):
        """Exclude name field if user is logged in"""
        fields = (getattr(self, str(f)) for f in self._fields)
        if flask_login.current_user.is_authenticated:
            fields = filter(lambda f: f.name != 'name', fields)
        return iter(fields)

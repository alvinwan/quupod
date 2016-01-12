from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
import wtforms as wtf
from queue.staff.forms import AssignmentForm, ProblemForm
from queue.staff.models import Inquiry, User
import flask_login


class SigninForm(wtf.Form):
    username = wtf.StringField()
    password = wtf.PasswordField()


class UserForm(ModelForm):
    """form for user signup and signin"""
    class Meta:
        model = User
        only = ('name', 'email', 'username', 'password')


class InquiryForm(ModelForm):
    """form for placing inquiries"""
    class Meta:
        model = Inquiry
        only = ('name', 'question')

    assignment = ModelFieldList(FormField(AssignmentForm))
    problem = ModelFieldList(FormField(ProblemForm))

    def __iter__(self):
        fields = (getattr(self, str(f)) for f in self._fields)
        if flask_login.current_user.is_authenticated:
            condition = lambda f: f.name != 'name'
            fields = filter(condition, fields)
        return iter(fields)

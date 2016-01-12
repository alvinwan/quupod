from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
import wtforms as wtf
from queue.staff.forms import AssignmentForm, ProblemForm
from queue.staff.models import Inquiry, User


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
        only = ('question',)

    assignment_id = ModelFieldList(FormField(AssignmentForm))
    problem_id = ModelFieldList(FormField(ProblemForm))

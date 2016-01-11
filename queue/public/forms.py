from wtforms_alchemy import ModelForm, ModelFieldList
from wtforms.fields import FormField
from queue.staff.forms import AssignmentForm, ProblemForm
from queue.staff.models import Request, User


class UserForm(ModelForm):
    """form for user signup and signin"""
    class Meta:
        model = Request
        only = ('name', 'email', 'username', 'password')


class RequestForm(ModelForm):
    """form for placing requests"""
    class Meta:
        model = Request
        only = ('question')

    assignment_id = ModelFieldList(FormField(AssignmentForm))
    problem_id = ModelFieldList(FormField(ProblemForm))

from django import forms
from grader.models import UserRole, StudentDetail
from django.contrib.auth.models import User

class LoginForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = None

    password = forms.CharField(widget = forms.PasswordInput(attrs = {'minlength': '8', 'class': 'form-control', 'id': "password", 'name': 'password', 'data-eye': 'true'}))

    class Meta():
        model = User
        fields = ('username', 'password')

        widgets = {
            'username': forms.TextInput(attrs = {'class': 'form-control', 'id': 'username', 'name': 'username'}),
        }


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = None

    password = forms.CharField(widget = forms.PasswordInput(attrs = {'minlength': '8', 'class': 'form-control', 'id': "password", 'name': 'password', 'data-eye': 'true'}))

    class Meta():
        model = User
        fields = ('username', 'email', 'password')

        widgets = {
            'username': forms.TextInput(attrs = {'class': 'form-control', 'id': 'username', 'name': 'username'}),
            'email': forms.EmailInput(attrs = {'class': 'form-control', 'id': 'email', 'name': 'email'}),
        }

class UserRoleForm(forms.ModelForm):

    class Meta():
        model = UserRole
        fields = ('role',)

        roleChoices = [
            ('student', 'Student'),
            ('teacher', 'Teacher')
        ]

        widgets = {
            'role': forms.Select(choices = roleChoices, attrs = {'class': 'form-select form-control', 'id': 'role', 'name': 'role'}),
        }

class StudentDetailsForm(forms.ModelForm):

    class Meta():
        model = StudentDetail
        fields = ('semester', 'branch')

        semesterChoices = [
            ('1', 'I'),
            ('2', 'II'),
            ('3', 'III'),
            ('4', 'IV'),
            ('5', 'V'),
            ('6', 'VI'),
            ('7', 'VII'),
            ('8', 'VIII'),
        ]
        branchChoices = [
            ('cse', 'Computer Science and Engineering'),
            ('ese', 'Electronics and Communications Engineering'),
            ('me', 'Mechanical Engineering'),
            ('ee', 'Electrical Engineering'),
            ('ce', 'Civil Engineering'),
        ]

        widgets = {
            'semester': forms.Select(choices = semesterChoices, attrs = {'class': 'form-select form-control', 'id': 'semester', 'name': 'semester'}),
            'branch': forms.Select(choices = branchChoices, attrs = {'class': 'form-select form-control', 'id': 'branch', 'name': 'branch'}),
        }

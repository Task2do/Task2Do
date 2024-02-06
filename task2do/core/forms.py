from datetime import timedelta, date

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import Worker, Manager, Project, Task, STATUS_CHOICES
from django_select2.forms import Select2MultipleWidget


class UserRegistrationForm(forms.ModelForm):
    USER_TYPE_CHOICES = (
        ('manager', 'מנהל משימה'),
        ('worker', 'משתמש'),
    )

    username = forms.CharField(label='שם משתמש')
    password = forms.CharField(widget=forms.PasswordInput, label='סיסמא')
    email = forms.EmailField(label='אימייל')
    first_name = forms.CharField(label='שם פרטי')
    last_name = forms.CharField(label='שם משפחה')
    birth_date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        label='תאריך לידה'
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, label='סוג משתמש')

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'birth_date']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists. Please choose another one.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password_errors = []
        if len(password) < 8:
            password_errors.append(ValidationError("Password must be at least 8 characters long."))
        if not re.search(r'\d', password):
            password_errors.append(ValidationError("Password must contain at least one number."))
        if not re.search(r'\D', password):
            password_errors.append(ValidationError("Password must contain at least one letter."))
        if not re.search(r'\W', password):
            password_errors.append(ValidationError("Password must contain at least one symbol."))
        if password_errors:
            raise ValidationError(password_errors)
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'manager':
            if Manager.objects.filter(personal_data__user__email=email).exists():
                raise ValidationError("Email already exists for this user type. Please choose another one.")
        else:
            if Worker.objects.filter(personal_data__user__email=email).exists():
                raise ValidationError("Email already exists for this user type. Please choose another one.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        return last_name

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future.")
        elif birth_date > date.today() - timedelta(days=6 * 365):
            raise ValidationError("You must be at least 6 years old to register.")
        elif birth_date < date.today() - timedelta(days=120 * 365):
            raise ValidationError("Birth date cannot be more than 120 years in the past.")
        return birth_date


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'members']
        widgets = {
            'members': Select2MultipleWidget
        }

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager')
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        self.fields['members'].queryset = Worker.objects.filter(managers=manager)



class TaskEditForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[(CHOICE, choice) for (CHOICE, choice) in STATUS_CHOICES if CHOICE != 'CANCELED'])

    class Meta:
        model = Task
        fields = ['status', 'title', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super(TaskEditForm, self).__init__(*args, **kwargs)
        if not self.instance.parent_task:
            self.fields['title'].disabled = True
            self.fields['description'].disabled = True
            self.fields['is_active'].disabled = True

class ManagerTaskEditForm(forms.ModelForm):
    status = forms.ChoiceField(choices=[(CHOICE, choice) for (CHOICE, choice) in STATUS_CHOICES])

    class Meta:
        model = Task
        fields = ['status', 'title', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super(ManagerTaskEditForm, self).__init__(*args, **kwargs)
        if self.instance.parent_task:
            self.fields['title'].disabled = True
            self.fields['description'].disabled = True
            self.fields['is_active'].disabled = True

class SubtaskDivisionForm(forms.Form):
    num_subtasks = forms.IntegerField(min_value=1, max_value=10, label='Number of Subtasks')

class SubtaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status']

SubtaskFormSet = forms.formset_factory(SubtaskForm, extra=1)


class ProjectChangeForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'is_active']
        # todo: add due date


from django import forms
from .models import Task, Worker

class TaskCreationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'assigned_to', 'due_date', 'description']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id')
        super(TaskCreationForm, self).__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = Worker.objects.filter(projects__id=project_id)
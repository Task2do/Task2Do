from datetime import timedelta, date

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

from .models import Worker, Manager


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

from .models import Project
class CreateProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(queryset=Worker.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Project
        fields = ['name', 'description', 'members']
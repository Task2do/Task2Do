from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists. Please choose another one.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'\D', password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r'\W', password):
            raise ValidationError("Password must contain at least one symbol.")
        return password

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()
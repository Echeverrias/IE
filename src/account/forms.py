from django import forms
from django.forms import ValidationError
from django.core import exceptions
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except exceptions.ValidationError as e:
            raise ValidationError('El email no es válido')
        if User.objects.filter(email__exact=email):
            raise ValidationError('El email está asociado a otro usuario')
        else:
            return email
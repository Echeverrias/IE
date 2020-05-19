from django.test import TestCase
from account.models import Account
from account.forms import SignInForm
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User

print(__file__)
class TestSignInForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(user_name='user', email="user@gmail.com")

    def test_register_an_existing_email(self):
        form_data = {
                     'user_name': 'test',
                     'password1': '1qw23er4',
                     'password2': '1qw23er4',
                     'email': TestSignInForm.user.email
        }
        form = SignInForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_an_existing_user_name(self):
        form_data = {
            'user_name': TestSignInForm.user.user_name,
            'password1': '1qw23er4',
            'password2': '1qw23er4',
            'email': 'test@gmail.com'
        }
        form = SignInForm(form_data)
        self.assertFalse(form.is_valid())




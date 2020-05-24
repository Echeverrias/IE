from django.test import TestCase
from account.forms import RegisterForm
from django.contrib.auth.models import User

class TestRegisterForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user', email="user@test.com")

    def test_register_an_existing_email(self):
        form_data = {
                     'username': 'new_user',
                     'password1': '1qw23er4',
                     'password2': '1qw23er4',
                     'email': self.user.email
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_an_existing_username(self):
        form_data = {
            'username': self.user.username,
            'password1': '1qw23er4',
            'password2': '1qw23er4',
            'email': 'new_email@test.com'
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_an_invalid_email(self):
        form_data = {
            'username': "new_user",
            'password1': '1qw23er4',
            'password2': '1qw23er4',
            'email': 'new_email.test.com'
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_an_invalid_password(self):
        form_data = {
            'username': "new_user",
            'password1': 'qwe',
            'password2': 'qwe',
            'email': 'new_email@test.com'
        }
        form = RegisterForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_a_valid_new_user(self):
        form_data = {
            'username': "new_user",
            'password1': 'ABRAcadabra555',
            'password2': 'ABRAcadabra555',
            'email': 'new_email@test.com'
        }
        form = RegisterForm(form_data)
        self.assertTrue(form.is_valid())



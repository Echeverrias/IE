from django.test import TestCase
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from core.management.commands.initadmin import Command

class TestInitAdmin(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.c = Command()

    def test_handle(self):
        # Not enough arguments
        options={
            'username':'user'
        }
        try:
            exception = None
            self.c.handle(**options)
        except Exception as e:
            exception = e
        self.assertEqual(type(exception), CommandError)
        # The email is invalid
        options.update({'email': 'inavid_email', 'password': 'pw'})
        try:
            exception = None
            self.c.handle(**options)
        except Exception as e:
            exception = e
        self.assertEqual(type(exception), CommandError)
        # There is an user with the same username
        User.objects.create(username='user', password='pw')
        try:
            exception = None
            self.c.handle(**options)
        except Exception as e:
            exception = e
        self.assertEqual(type(exception), CommandError)
        # A valid user
        options.update({'username': 'new', 'email': 'email@test.com', 'password': 'pw'})
        try:
            exception = None
            self.c.handle(**options)
        except Exception as e:
            exception = e
        self.assertIsNone(exception)
        try:
            exception = None
            user = User.objects.get(username='new')
        except Exception as e:
            exception = e
        self.assertIsNone(exception)
        self.assertIsNotNone(user)
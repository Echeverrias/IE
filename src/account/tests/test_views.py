from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class TestAccountViews(TestCase):

   @classmethod
   def setUpTestData(cls):
      cls.username = 'user'
      cls.admin_username = 'root'
      cls.password='1qw23er45t'
      cls.email1='user@gmail.com'
      cls.email2='root@gmail.com'
      cls.admin_user = User.objects.create_user(username=cls.admin_username,
                                            password=cls.password,
                                            email=cls.email2,
                                            is_superuser=True)
      cls.admin_user.save()
      cls.user = User.objects.create_user(username=cls.username,
                                      password=cls.password,
                                      email=cls.email1)
      cls.user.save()

   def test_login_get_view(self):
      resp = self.client.get(reverse('login'))
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'account/login.html')

   def test_login_post_right_view(self):
      data = {'username': self.username, 'password': self.password}
      resp = self.client.post(reverse('login'), data=data, follow=True)
      self.assertEqual(resp.status_code, 200)
      self.assertRedirects(resp, '/home/', status_code=302, target_status_code=200)
      self.assertTemplateUsed(resp, 'index.html')
      # The user has logged and request the login page again
      resp = self.client.post(reverse('login'), data=data, follow=True)
      self.assertEqual(resp.status_code, 200)
      self.assertRedirects(resp, '/home/', status_code=302, target_status_code=200)
      self.assertTemplateUsed(resp, 'index.html')

   def test_login_post_wrong_view(self):
      data = {'username': '?', 'password': '?'}
      resp = self.client.post(reverse('login'), data=data)
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'account/login.html')

   def test_register_get_view(self):
      resp = self.client.get(reverse('register'))
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'account/register.html')

   def test_register_post_wrong(self):
      form_data = {
         'username': self.username,
         'password1': '1qw23er4',
         'password2': '1qw23er4',
         'email': self.email1,
      }
      resp = self.client.post(reverse('register'), data=form_data, follow=True)
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'account/register.html')

   def test_register_post_right(self):
      form_data = {
         'username': 'new_user',
         'password1': 'ABRAcadabra555',
         'password2': 'ABRAcadabra555',
         'email': 'new_email@test.com',
      }
      resp = self.client.post(reverse('register'), data=form_data, follow=True)
      self.assertEqual(resp.status_code, 200)
      self.assertRedirects(resp, '/home/', status_code=302, target_status_code=200)
      self.assertTemplateUsed(resp, 'index.html')

   def test_logout_get_view(self):
      resp = self.client.get(reverse('logout'), follow=True)
      self.assertEqual(resp.status_code, 200)
      self.assertRedirects(resp, '/account/login/', status_code=302, target_status_code=200)
      self.assertTemplateUsed(resp, 'account/login.html')

   def test_logout_user_view(self):
      data = {'username': self.username, 'password': self.password}
      self.client.post(reverse('login'), data=data)
      resp = self.client.get(reverse('logout'), follow=True)
      self.assertEqual(resp.status_code, 200)
      self.assertRedirects(resp, '/account/login/', status_code=302, target_status_code=200)
      self.assertTemplateUsed(resp, 'account/login.html')




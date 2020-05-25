from django.test import TestCase
from job.filters import JobFilter
from job.models import Job, Company
import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.contrib.auth.models import User



class JobListViewTest(TestCase):

   @classmethod
   def setUpTestData(cls):
      cls.username = 'user'
      cls.admin_username = 'root'
      cls.password='1qw23er45t'
      test_user1 = User.objects.create_user(username='root', password='1qw23er45t', is_superuser=True)
      test_user1.save()
      test_user2 = User.objects.create_user(username='user', password='1qw23er45t')
      test_user2.save()
      for i in range(0,25):
         Job.objects.create(id=i, name=str(i), vacancies=1)

   def test_view_need_login(self):
      resp = self.client.get(reverse('job_list'))
      self.assertEqual(resp.status_code, 302)
      self.assertRedirects(resp, '/account/login/?next=' + reverse('job_list'))

   def test_job_list(self):
      self.client.login(username='root', password='1qw23er45t')
      #resp = self.client.get(reverse('job_list'))
      resp = self.client.get('/job/list/')
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'job/query_form.html')

   def test_pagination_is_ten(self):
      self.client.login(username=JobListViewTest.admin_username, password=JobListViewTest.password)
      resp = self.client.get(reverse('job_list'))
      self.assertEqual(resp.status_code, 200)
      self.assertIn('is_paginated', resp.context)
      self.assertTrue(resp.context['is_paginated'] == True)
      self.assertEqual(len(resp.context['job_list']), 20)

   def test_lists_all_jobs(self):
      self.client.login(username=JobListViewTest.admin_username, password=JobListViewTest.password)
      resp = self.client.get('/job/list/?page=2')
      self.assertEqual(resp.status_code, 200)
      self.assertIn('is_paginated', resp.context)
      self.assertTrue(resp.context['is_paginated'])
      self.assertEqual(len(resp.context['job_list']), 5)

   def test_lists_detail_job(self):
      self.client.login(username=JobListViewTest.admin_username, password=JobListViewTest.password)
      resp = self.client.get('/job/detail/1/')
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'job/job_detail.html')
      job = Job.objects.get(id=1)
      self.assertEqual(resp.context['job'], job)

   def test_lists_filter_jobs(self):
      #  Not available jobs:
      now = timezone.localtime(timezone.now())
      rel = relativedelta(days=5)
      some_days_ago = now - rel
      Job.objects.create(id=71, name='4', expiration_date=some_days_ago)
      Job.objects.create(id=81, functions="4", state=Job.STATE_CLOSED)
      filter_data = {'text': "4",}
      self.client.login(username=JobListViewTest.admin_username, password=JobListViewTest.password)
      resp = self.client.get(reverse('job_list'), filter_data)
      self.assertEqual(resp.status_code, 200)
      self.assertEqual(len(resp.context['job_list']), 3)
      self.assertIn('is_paginated', resp.context)
      self.assertFalse(resp.context['is_paginated'])
from django.test import TestCase
from task.models import Task
from job.models import Job, Company
import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.contrib.auth.models import User
from multiprocessing import  Queue, Process
from task.tasks import SpiderProcess




class TestRunCrawlerView(TestCase):

   @classmethod
   def setUpTestData(cls):
      cls.admin_username = 'root'
      cls.username = 'user'
      cls.password='1qw23er45t'
     # cls.root_user = User.objects.create(username=JobListViewTest.admin_username, password=JobListViewTest.password, is_superuser=True)
      #cls.user = User.objects.create(username=JobListViewTest.username, password=JobListViewTest.password)
      admin = User.objects.create_user(username=cls.admin_username, password=cls.password, is_staff=True, is_superuser=True)
      admin.save()
      user = User.objects.create_user(username=cls.username , password=cls.password)
      user.save()
      cls.sp = SpiderProcess.get_instance()
   """
   def test_view_need_login(self):
      resp = self.client.get(reverse('scrapping'))
      self.assertEqual(resp.status_code, 302)
      self.assertRedirects(resp, '/admin/login/?next=' + reverse('scrapping'))

   def test_view_need_admin_permission(self):
      self.client.login(username=self.username, password=self.password)
      resp = self.client.get(reverse('scrapping'))
      self.assertEqual(resp.status_code, 302)
      self.assertRedirects(resp, '/admin/login/?next=' + reverse('scrapping'))

   def test_view_with_admin_permission(self):
      self.client.login(username=self.admin_username, password=self.password)
      resp = self.client.get(reverse('scrapping'))
      self.assertEqual(resp.status_code, 200)
      self.assertTemplateUsed(resp, 'task/main.html')

   def test_job_view(self):
      self.client.login(username=self.admin_username, password=self.password)
      model = 'job'
      resp = self.client.get(f'/task/scrapping/{model}/')
      self.assertEqual(resp.status_code, 200)
      self.assertEqual(resp.context['model'], model)
      self.assertTemplateUsed(resp, 'task/main.html')

   def test_task_incomplete(self):
      Task.objects.create(pid=555, state=Task.STATE_RUNNING, type=Task.TYPE_CRAWLER)
      self.client.login(username=self.admin_username, password=self.password)
      resp = self.client.get(reverse('scrapping'))
      task = resp.context['tasks'][0]
      self.assertEqual(task.pid, 555)
      self.assertEqual(task.state, Task.STATE_INCOMPLETE)
      self.assertFalse(resp.context['is_running'])
      self.assertFalse(resp.context['ajax'])
      self.assertTemplateUsed(resp, 'task/main.html')
   
   def test_finished_task_ajax_request(self):
      self.client.login(username=self.admin_username, password=self.password)
      task = Task.objects.create(pid=555, state=Task.STATE_RUNNING, type=Task.TYPE_CRAWLER)
      resp = self.client.get('/task/scrapping/?AJAX')
      self.assertFalse(resp.context['is_running'])
      self.assertTrue(resp.context['ajax'])
      self.assertTemplateUsed(resp, 'task/init_ajax.html')
   """
   def test_running_task_ajax_request(self):
      self.client.login(username=self.admin_username, password=self.password)
      task = Task.objects.create(pid=555, state=Task.STATE_RUNNING, type=Task.TYPE_CRAWLER)
      self.sp._id_task = task.pk
      self.sp._process = Process()
      q_items = Queue()
      q_items.put(20)
      self.sp._q = q_items
      qis_scrapping = Queue()
      qis_scrapping.put(True)
      self.sp._qis_scrapping = q_items
      resp = self.client.get('/task/scrapping/?AJAX')
      self.assertTrue(resp.context['ajax'])
      self.assertEqual(resp.context['scraped_items_number'], 20)
      self.assertTemplateUsed(resp, 'task/info_crawler_task.html')
      self.assertTrue(resp.context['is_running'])



from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from multiprocessing import  Queue, Process
from task.models import Task
from job.models import Job, Company
from task.tasks import SpiderProcess
from .fake_tasks import FakeSpiderProcess
from scrapy.spiders import Spider

class FakeSpider(Spider):
   name = "fake_spider"

class TestSpiderProcess(TestCase):

   @classmethod
   def setUpTestData(cls):
      cls.sp = FakeSpiderProcess.get_instance()
      cls.fake_user = User.objects.create_user(username='fake_user',
                                      password='1qw23er45ty6',
                                      email='fake@fakee.com')
      cls.fake_user.save()

   def tearDown(self):
      self.sp.tearDown()

   def test_get_actual_task(self):
      # There isn't any task:
      self.assertIsNone(self.sp.get_actual_task())
      # There is a task:
      data = self.sp.simulate_running_process()
      self.assertEqual(self.sp.get_actual_task(), data['task'])

   def test_latest_task_when_a_task_is_running(self):
      """
         Must return the actual task (the running task)
      """
      Task.objects.create(name="old task finished", state=Task.STATE_FINISHED, type=Task.TYPE_CRAWLER)
      data = self.sp.simulate_running_process()
      self.assertEqual(self.sp.get_latest_task(), data['task'])

   def test_latest_task_when_there_is_not_a_task(self):
      """
         Must return the last task from the db
      """
      Task.objects.create(name="old task", state=Task.STATE_FINISHED, type=Task.TYPE_CRAWLER)
      task = Task.objects.create(name="latest task", state=Task.STATE_FINISHED, type=Task.TYPE_CRAWLER)
      self.assertEqual(self.sp.get_latest_task(), task)

   def test_update_last_db_task_if_is_incomplete(self):
      """
         If there is in the database a task with state equal 'STATE_RUNNING' and it isn't the
         SpiderProcess actual task, the state of the task is updated to 'STATE_INCOMPLETE'
      """
      incomplete_task = Task.objects.create(name="old task", state=Task.STATE_RUNNING, type=Task.TYPE_CRAWLER)
      self.sp._update_last_db_task_if_is_incomplete(incomplete_task, self.sp.get_actual_task())
      latest_task = Task.objects.get_latest_crawler_task()
      self.assertEqual(latest_task.id, incomplete_task.id)
      self.assertEqual(latest_task.state, Task.STATE_INCOMPLETE)
      data = self.sp.simulate_running_process()
      actual_task = data['task']
      self.sp._update_last_db_task_if_is_incomplete(actual_task , self.sp.get_actual_task())
      latest_task = Task.objects.get_latest_crawler_task()
      self.assertEqual(latest_task.id, actual_task.id)
      self.assertEqual(latest_task.state, Task.STATE_RUNNING)

   def test_empty_queue(self):
      q = Queue()
      q.put(1);q.put(2)
      self.sp._empty_queue(q)
      self.assertEqual(q.qsize(),0)

   def test_close_queue(self):
      q = Queue()
      self.sp._close_queue(q)
      self.assertEqual(q.qsize(),0)
      try:
         exception = None
         q.empty()
      except Exception as e:
         exception = e
      self.assertIsNotNone(exception)

   def test_empty_and_close_queue(self):
      q = Queue()
      q.put(1);
      q.put(2)
      self.sp._empty_and_close_queue(q)
      self.assertEqual(q.qsize(),0)
      try:
         exception = None
         q.empty()
      except Exception as e:
         exception = e
      self.assertIsNotNone(exception)

   def test_init_process(self):
      self.sp._init_process(FakeSpider, self.fake_user)
      self.assertIsNotNone(self.sp._process)
      self.assertIsNotNone(self.sp._id_task)
      self.assertIsNotNone(self.sp._qitems_number)
      self.assertIsNotNone(self.sp._qis_scraping)
      last_crawler_task = Task.objects.get_latest_crawler_task()
      self.assertEqual(self.fake_user,  last_crawler_task.user)
      self.assertFalse(self.sp.is_scraping())

   def test_is_scraping(self):
      self.assertFalse(self.sp.is_scraping())
      self.sp._init_process(FakeSpider, self.fake_user)
      self.assertFalse(self.sp.is_scraping())
      self.sp.simulate_running_process()
      self.assertTrue(self.sp.is_scraping())

   def test_reset_process(self):
      self.sp.simulate_running_process()
      self.sp._reset_process()
      self.assertIsNone(self.sp._process)
      self.assertIsNone(self.sp._id_task)
      self.assertEqual(self.sp._qitems_number.qsize(), 0)
      self.assertEqual(self.sp._qis_scraping.qsize(), 0)
      self.assertFalse(self.sp._is_resetting)
      self.assertFalse(self.sp.is_scraping())

   def test_update_task(self):
      task = Task.objects.create(name='fake', state=Task.STATE_RUNNING)
      self.sp._update_task(task.id, data={'state': Task.STATE_FINISHED})
      self.assertEqual(Task.objects.get(id=task.id).state, Task.STATE_FINISHED)
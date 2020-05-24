from django.test import TestCase
from task.models import Task

class TestTask(TestCase):

    @classmethod
    def setUpTestData(cls):
        # The fake tasks have been created by order of the field name
        ct1 = Task.objects.create(type=Task.TYPE_CRAWLER, state=Task.STATE_FINISHED, name='company')
        ct2 = Task.objects.create(type=Task.TYPE_CRAWLER, state=Task.STATE_FINISHED, name='job')
        ct3 = Task.objects.create(type=Task.TYPE_CRAWLER, state=Task.STATE_RUNNING, name='job')
        cls.crawler_tasks = [ct1, ct2, ct3]
        cls.finished_crawler_tasks = [ct1, ct2]
        cls.latest_crawler_task = ct3
        cls.latest_crawler_tasks = [ct1, ct3]
        cls.latest_finished_crawler_task = ct2
        cls.latest_finished_crawler_tasks = [ct1, ct2]

    def test_crawler_tasks(self):
        qs = Task.objects.crawler_tasks()
        l = self.crawler_tasks
        self.assertEqual(qs.count(), len(l))
        for task in l:
            self.assertEqual(qs.get(id=task.id), task)

    def test_finished_crawler_tasks(self):
        qs = Task.objects.finished_crawler_tasks()
        l = self.finished_crawler_tasks
        self.assertEqual(qs.count(), len(l))
        for task in l:
            self.assertEqual(qs.get(id=task.id), task)

    def test_get_latest_crawler_task(self):
        task = Task.objects.get_latest_crawler_task()
        self.assertEqual(task, self.latest_crawler_task)

    def test_get_latest_crawler_tasks(self):
        l = Task.objects.get_latest_crawler_tasks()
        l_ = self.latest_crawler_tasks
        self.assertEqual(len(l), len(l_))
        for task, task_ in zip(l,l_):
            self.assertEqual(task, task_)

    def test_get_latest_finished_crawler_task(self):
        task = Task.objects.get_latest_finished_crawler_task()
        self.assertEqual(task, self.latest_finished_crawler_task)

    def test_get_latest_finished_crawler_tasks(self):
        l = Task.objects.get_latest_finished_crawler_tasks()
        l_ = self.latest_finished_crawler_tasks
        self.assertEqual(len(l), len(l_))
        for task, task_ in zip(l, l_):
            self.assertEqual(task, task_)


from django.test import TestCase
from task.models import Task

class TestTask(TestCase):

    def test_states(self):
        running_task = Task.objects.create(state=Task.STATE_RUNNING)
        finished_task = Task.objects.create(state=Task.STATE_FINISHED)
        self.assertTrue(running_task.is_running)
        self.assertTrue(finished_task.is_completed)
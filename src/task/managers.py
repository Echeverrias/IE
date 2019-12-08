from django.db import models
from django.db.models import F
from .queries import TaskQuerySet
from datetime import date


"""
https://medium.com/@jairvercosa/manger-vs-query-sets-in-django-e9af7ed744e0
https://docs.djangoproject.com/en/2.2/topics/db/managers/
"""
class TaskManager(models.Manager):


    def get_queryset(self):

        # Don't apply filters, don't return a modified queryset
        return TaskQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints
        )

    def crawler_tasks(self):
        return self.get_queryset().crawler_tasks()

    def finished_crawler_tasks(self):
        return self.get_queryset().finished_crawler_tasks()

    def get_latest_crawler_task(self):
        return self.get_queryset().get_latest_crawler_task()

    def get_latest_finished_crawler_task(self):
        return self.get_queryset().get_latest_finished_crawler_task()


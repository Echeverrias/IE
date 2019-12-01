##from .models import Job
from django.db import models
from django.db.models import Q, F
from datetime import date

TYPE_CRAWLER = 'Crawler'


class TaskQuerySet(models.QuerySet):

    def get_latest_crawler_task(self):
        return self.filter(type__iexact=TYPE_CRAWLER).latest('created_at')

    def crawler_tasks(self):
        return self.filter(type__iexact=TYPE_CRAWLER)


##from .models import Job
from django.db import models
from django.db.models import Q, F
from datetime import date

TYPE_CRAWLER = 'Crawler'
STATE_FINISHED = 'Terminada'


class TaskQuerySet(models.QuerySet):

    def crawler_tasks(self):
        return self.filter(type__iexact=TYPE_CRAWLER)

    def finished_crawler_tasks(self):
        return self.filter(type__iexact=TYPE_CRAWLER).filter(state__iexact=STATE_FINISHED)

    def get_latest_crawler_task(self):
        return self.crawler_tasks().latest('created_at')

    def get_latest_finished_crawler_task(self):
        return self.finished_crawler_tasks().latest('created_at')


from django.db import models
from django.db.models import Q, F, Count
from datetime import date

TYPE_CRAWLER = 'Crawler'
STATE_FINISHED = 'Terminada'

class TaskQuerySet(models.QuerySet):

    def crawler_tasks(self):
        return self.filter(type__iexact=TYPE_CRAWLER)

    def finished_crawler_tasks(self):
        return self.filter(type__iexact=TYPE_CRAWLER).filter(state__iexact=STATE_FINISHED)

    def get_latest_crawler_task(self):
        try:
            return self.crawler_tasks().latest('created_at')
        except Exception as e:
            return None

    def get_latest_crawler_tasks(self):
        try:
            distinct = self.crawler_tasks().values('name').order_by('name').annotate(name_count=Count('name'))
            names = [name.get('name') for name in distinct]
            tasks =  [self.crawler_tasks().filter(name=name).latest('created_at') for name in names]
            pks = [task.pk for task in tasks if task]
            qs =  self.filter(pk__in=pks).order_by('created_at')
            return qs
        except Exception as e:
            return self.none()

    def get_latest_finished_crawler_task(self):
        try:
            return self.finished_crawler_tasks().latest('created_at')
        except Exception as e:
            return None

    def get_latest_finished_crawler_tasks(self):
        try:
            distinct = self.crawler_tasks().values('name').order_by('name').annotate(name_count=Count('name'))
            names = [name.get('name') for name in distinct]
            tasks =  [ self.finished_crawler_tasks().filter(name=name).latest('created_at') for name in names]
            pks = [task.pk for task in tasks if task]
            qs = self.filter(pk__in=pks).order_by('created_at')
            return qs
        except Exception as e:
            return self.none()
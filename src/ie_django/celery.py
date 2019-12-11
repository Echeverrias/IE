from __future__ import absolute_import
import os
from celery import Celery, shared_task, current_app
from celery.schedules import crontab

from django.conf import settings

"""
https://medium.com/@ksarthak4ever/django-handling-periodic-tasks-with-celery-daaa2a146f14
https://djangopy.org/how-to/handle-asynchronous-tasks-with-celery-and-django?source=post_page-----daaa2a146f14----------------------
"""
# celery -A ie_django beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ie_django.settings')
app = Celery('ie_django')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print('setup_periodic_tasks')
    sender.add_periodic_task(crontab(minute='*/10', hour='*'), periodic_task.s('run_crawler'), name='pt')


@app.task
def periodic_task(taskname, *args):
    from task.tasks import run_crawler
    print('PERIODIC TASK')
    if taskname == 'run_crawler':
        run_crawler()




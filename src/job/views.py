from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import time
from .models import Job
from .filters import JobFilter
from .init_db import initialize_database


# Scrapy
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from multiprocessing import Process, Queue
from ie_scrapy.spiders.ie import InfoempleoSpider
from ie_scrapy.spiders.companies import InfoempleoCompaniesSpider


@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    model = Job
    context_object_name = 'job_list'  # your own name for the list as a template variable
    template_name = 'job/query_form.html' #'job/job_list.html'  # Specify your own template name/location
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        print(f'JobListView.get_queryset')
        qs = super(JobListView, self).get_queryset()
        qs = qs.prefetch_related('cities')
        self.job_filtered_list = JobFilter(self.request.GET, qs)
        return self.job_filtered_list.qs

    def get_context_data(self, **kwargs):
         # Call the base implementation first to get the context
        context = super(JobListView, self).get_context_data(**kwargs)
         # Create any data and add it to the context
        context['form'] = self.job_filtered_list.form
        return context


if __name__ != '__main__':
    try:
        initialize_database()
    except Exception as e:
        print(e)

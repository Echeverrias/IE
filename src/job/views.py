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
from background_task import background
from ie_scrapy.spiders.ie import InfoempleoSpider
from ie_scrapy.spiders.companies import InfoempleoCompaniesSpider


@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    model = Job
    context_object_name = 'job_list'  # your own name for the list as a template variable
    #queryset = Job.objects.all()[0:50] # Get 5 books containing the title war
    template_name = 'job/query_form.html' #'job/job_list.html'  # Specify your own template name/location
    paginate_by = 10


    def get_queryset(self, *args, **kwargs):
        print(f'JobListView.get_queryset')
        qs = super(JobListView, self).get_queryset()
        qs = qs.prefetch_related('cities')
        self.job_filtered_list = JobFilter(self.request.GET) # JobFilter(self.request.GET, queryset=qs)
        return self.job_filtered_list.qs


    def get_context_data(self, **kwargs):
         # Call the base implementation first to get the context
        context = super(JobListView, self).get_context_data(**kwargs)
         # Create any data and add it to the context
        context['form'] = self.job_filtered_list.form
        return context


#@user_passes_test(lambda u: u.is_superuser)
@staff_member_required
def run_crawler(request):
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;

    def f(q):
        try:
            crawler_settings = get_project_settings()
            runner = CrawlerRunner(crawler_settings)
            dispatcher.connect(lambda _: print('finish'), signal=signals.spider_closed)#'item_scraped'
            dispatcher.connect(lambda _: print('item scraped'), signal=signals.item_scraped)#'item_scraped'
            deferred = runner.crawl(InfoempleoSpider)
            deferred.addBoth(lambda _: reactor.stop())
            print('reactor...')
            reactor.run()
            print('run!!!!!')
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        print('result is not None')
        print(result)
    else:
        print('result is  None')
        print(result)
    return HttpResponse("<h1>%Crawler running...</h1><a href='admin/'>Go to admin</a>")

@background(schedule=5)
def _process_async():
    time.sleep(3)
    print('process_async')
    #process = ProcessExecutor()
    #process.start()
    #print('process_async started')
    #process.join()
    #print('process_async joined')
def run(request):
    _process_async()
    #print(f'ProcessExecutor.count: {ProcessExecutor.count}')
    print('next!!')
    return HttpResponse("<h1>Process_async executing...</h1><a href='/'>Inicio</a>")


if __name__ != '__main__':
    try:
        initialize_database()
    except Exception as e:
        print(e)

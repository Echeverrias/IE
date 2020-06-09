from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from ie_scrapy.spiders.ie import InfoempleoSpider
from ie_scrapy.spiders.companies import InfoempleoCompaniesSpider
from .models import Task
from .tasks import SpiderProcess
from job.models import Job
import  logging
logging.getLogger().setLevel(logging.DEBUG)


@staff_member_required
def run_crawler_view(request, model=None):
    sp = SpiderProcess.get_instance()
    is_stopped = False
    is_running = sp.is_scraping()
    req = ''
    try:
        spider = InfoempleoCompaniesSpider if 'company' in model.lower() else InfoempleoSpider
    except:
        spider = None
    if request.GET.get('crawl', None):
        if not is_running:
            user = User.objects.get(username=request.user)
            sp.start(spider, user)
            is_running = True
        req = 'crawl'
    elif request.GET.get('stop', None):
        sp.stop()
        is_running = False
        is_stopped = True
    if request.GET.get('crawl', None) or 'AJAX' in request.GET or 'stop' in request.GET: # get a task at most
        last_task = sp.get_actual_task() or sp.get_latest_task()
        last_tasks = [last_task] if last_task else []
    else: # can get various tasks
        actual_task = sp.get_actual_task()
        last_tasks = [actual_task] if (actual_task and is_running) else sp.get_latest_tasks()
        last_tasks = [task  for task in last_tasks if task.name == spider.name] if spider else last_tasks
    scraped_items_number = sp.get_scraped_items_number()
    context = {
        'model': model,
        'tasks': last_tasks,
        'is_running': is_running,
        'p': sp.process and sp.process.pid,
        'running_state': Task.STATE_RUNNING,
        'ajax': False,
        'req': req,
        'scraped_items_number':  sp.get_scraped_items_number(),
        'is_stopped': is_stopped,
    }
    if 'AJAX' in request.GET: #request.is_ajax():
        context['ajax'] = True
        if (last_task.state == Task.STATE_RUNNING):
            logging.debug(f'{Task.STATE_RUNNING} - scraped_items_number:  {scraped_items_number}')
            template_name = 'task/info_crawler_task.html'
            return render(request, template_name, context)
        elif (last_task.state == Task.STATE_PENDING):
            return HttpResponse('not running')
        elif (last_task.state != Task.STATE_RUNNING):
            template_name = 'task/init_ajax.html'
            return render(request, template_name, context)
        else:
            return HttpResponse('not running')
    else:
        template_name = 'task/main.html'
        return render(request, template_name, context)
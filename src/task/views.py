from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from ie_scrapy.spiders.ie import InfoempleoSpider
from ie_scrapy.spiders.companies import InfoempleoCompaniesSpider
from .models import Task
from .tasks import SpiderProcess
from utilities.utilities import write_in_a_file #%

@staff_member_required
def run_crawler_view(request, model=None):
    sp = SpiderProcess.get_instance()
    req = ''
    write_in_a_file('view request - start', {}, 'tasks_view.txt')
    try:
        spider = InfoempleoCompaniesSpider if 'company' in model.lower() else InfoempleoSpider
    except:
        spider = None
    if request.GET.get('crawl', None):
        write_in_a_file('view request - start get request', {}, 'tasks_view.txt')
        user = User.objects.get(username=request.user)
        if not sp.is_scrapping():
            sp.start(spider, user)
        write_in_a_file('view request - end get request', {}, 'tasks_view.txt')
        req = 'crawl'
    if request.GET.get('crawl', None) or request.is_ajax(): # get a task at most
        last_task = sp.get_actual_task() or sp.get_latest_task()
        last_tasks = [last_task] if last_task else []
    else: # can get various tasks
        actual_task = sp.get_actual_task()
        last_tasks = (actual_task and [actual_task]) or sp.get_latest_tasks()
        last_tasks = [task  for task in last_tasks if task.name == spider.name] if spider else last_tasks
    write_in_a_file('view request - continue', {}, 'tasks_view.txt')
    is_running = sp.is_scrapping()
    write_in_a_file('view request - continue after call is_scrapping', {}, 'tasks_view.txt')
    write_in_a_file('view request - continue after call get_actual_task and get_latest_task', {}, 'tasks_view.txt')
    context = {
        'model': model,
        'tasks': last_tasks,
        'is_running': is_running,
        'p': sp.process and sp.process.pid,
        'running_state': Task.STATE_RUNNING,
        'ajax': False,
        'req': req,
        'scraped_items_number': -100,
    }
    write_in_a_file('view request - continue2', {'is_running': is_running, 'context': context}, 'tasks_view.txt')
    if is_running:
        context = { **context, **{
            'scraped_items_number': sp.get_scraped_items_number(),
            }
        }
    write_in_a_file('view request - continue3', {'is_running': is_running, 'context': context}, 'tasks_view.txt')
    if request.is_ajax():
        write_in_a_file('view request - ajax request', {'is_running': is_running, 'context': context}, 'tasks_view.txt')
        context['ajax'] = True
        if (last_task.state == Task.STATE_RUNNING):
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
        write_in_a_file('view request - not ajax request end', {'is_running': is_running, 'context': context}, 'tasks_view.txt')
        template_name = 'task/main.html'
        return render(request, template_name, context)

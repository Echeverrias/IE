from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from .tasks import CrawlProcess, bg_run_crawler
from .models import Task
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from utilities import write_in_a_file
from background_task.models import Task as tsk
from job.models import Job

import time


# Create your views here.
# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e


# python manage.py process_tasks
@staff_member_required
def run_crawler_view(request, *args):
    print('run_crawler_view');print();print()
    c = CrawlProcess.get_instance()
    req = ''
    write_in_a_file('view request - start', {}, 'tasks_view.txt')

    if request.GET.get('crawl', None) != None:
        print('run_crawler_view: crawl request');
        write_in_a_file('view request - start get request', {}, 'tasks_view.txt')
        user = User.objects.get(username=request.user)
        print(user)
        c.start(user)
        write_in_a_file('view request - end get request', {}, 'tasks_view.txt')
        print('CrawlProcess started !!!!')
        req = 'crawl'


    write_in_a_file('view request - continue', {}, 'tasks_view.txt')

    # se tosta aqui!!!!
    is_running = c.is_scrapping()

    write_in_a_file('view request - continue after call is_scrapping', {}, 'tasks_view.txt')

    print(f'run_crawler_view: c.is_scrapping: {is_running}')
    last_task = c.get_actual_task() or c.get_latest_task()

    write_in_a_file('view request - continue after call get_actual_task and get_latest_task', {}, 'tasks_view.txt')
    context = {
        'task': last_task,
        'is_running': is_running,
        'p': c.process and c.process.pid,
        'running_state': Task.STATE_RUNNING,
        'ajax': False,
        'req': req,
        'scraped_items_number': -100,
    }

    write_in_a_file('view request - continue2', {'is_running': is_running, 'context': context}, 'tasks_view.txt')

    if is_running:
        context = { **context, **{
            'scraped_items_number': c.get_scraped_items_number(),
            }

        }

    write_in_a_file('view request - continue3', {'is_running': is_running, 'context': context}, 'tasks_view.txt')

    if request.is_ajax():
        write_in_a_file('view request - ajax request', {'is_running': is_running, 'context': context}, 'tasks_view.txt')
        context['ajax'] = True
        print('AJAX request');print();print()
        print(f'context: {context}');print();print()
        if (last_task.state == Task.STATE_RUNNING):
            print(f'ajax request - state: {last_task.state}');
            print();
            print()
            template_name = 'task/info_crawler_task.html'
            #return JsonResponse(context)
            return render(request, template_name, context)
            #return render_to_response(template_name, context)
        elif (last_task.state == Task.STATE_PENDING):
            print(f'ajax request - state: {last_task.state}');print();print()
            return HttpResponse('not running')
        elif (last_task.state != Task.STATE_RUNNING):
            print(f'ajax request - state: {last_task.state}');print();print()
            template_name = 'task/init_ajax.html'
            #return render_to_response(template_name, context)
            return render(request, template_name, context)
        else:
            print(f'ajax request - state: {last_task.state}');print();print()
            return HttpResponse('not running')

    else:
        print(f'Context: {context}')
        write_in_a_file('view request - not ajax request end', {'is_running': is_running, 'context': context}, 'tasks_view.txt')
        template_name = 'task/main.html'
        return render(request, template_name, context)


def bg_run_crawler_view(request):
    print('')
    print('bg_run_crawler_view')
    print(dir(tsk))
    Job.objects.filter(state=Job.AREA_LEGAL).delete()
    bg_run_crawler(repeat=tsk.HOURLY)
    return HttpResponse(f'<h1>Running!! {tsk.HOURLY}</h1>')
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from .tasks import CrawlProcess, run_crawler_script
from .models import Task
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from utilities import write_in_a_file

import time


# Create your views here.
# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e


# python manage.py process_tasks
@staff_member_required
def run_crawler_view(request, *args):
    print('run_crawler_view');print();print()
    c = CrawlProcess.get_instance()
    req = ''
    if request.GET.get('crawl', None) != None:
        user = User.objects.get(username=request.user)
        print(user)
        c.start(user)
        print('CrawlProcess started !!!!')
        req = 'crawl'
    elif request.GET.get('stop', None) != None:
        print('run_crawler_view: stop request')
        write_in_a_file('view?stop: process will be stopped', {}, 'debug.txt')
        c.stop()
        write_in_a_file('view?stop: process stopped', {},'debug.txt')
        req = 'stop'

    is_running = c.is_scrapping()

    print(f'run_crawler_view: c.is_scrapping: {is_running}')
    last_task = c.get_actual_task() or c.get_latest_task()
    context = {
        'task': last_task,
        'is_running': is_running,
        'p': c.process and c.process.pid,
        'running_state': Task.STATE_RUNNING,
        'ajax': False,
        'req': req,
    }

    if is_running:
        context = { **context, **{
            'scraped_items_number': c.get_scraped_items_number(),
            }

        }

    if request.is_ajax():
        context['ajax'] = True
        print('AJAX request');print();print()
        print(f'context: {context}');print();print()
        if (last_task.state == Task.STATE_RUNNING):
            print(f'state: {last_task.state}')
            template_name = 'task/info_crawler_task.html'
            #return JsonResponse(context)
            return render(request, template_name, context)
            #return render_to_response(template_name, context)
        elif (last_task.state == Task.STATE_PENDING):
            print(f'state: {last_task.state}')
            print('ajax request');print();print()
            return HttpResponse('not running')
        elif (last_task.state != Task.STATE_RUNNING):
            print(f'state: {last_task.state}')
            template_name = 'task/init_ajax.html'
            #return render_to_response(template_name, context)
            return render(request, template_name, context)
        else:
            print(f'state: {last_task.state}')
            print('ajax request');
            return HttpResponse('not running')

    else:
        print(f'Context: {context}')
        write_in_a_file('view request', {'is_running': is_running, 'context': context}, 'debug.txt')
        template_name = 'task/main.html'
        return render(request, template_name, context)


def test_view(request):
    run_crawler_script()
    return HttpResponse('<h2>Crawler Script running</h2>')
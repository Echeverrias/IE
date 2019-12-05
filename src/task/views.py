from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from .tasks import CrawlProcess
from .models import Task
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.
# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e


# python manage.py process_tasks
@staff_member_required
def run_crawler_view(request, *args):
    print('run_crawler_view');print();print()
    c = CrawlProcess.get_instance()

    if request.GET.get('crawl', None) != None:
        user = User.objects.get(username=request.user)
        print(user)
        c.start(user)
        print('CrawlProcess started !!!!')
    elif request.GET.get('stop', None) != None:
        print('run_crawler_view: stop request')
        c.stop()

    is_running = c.is_scrapping()
    print(f'run_crawler_view: c.is_scrapping: {is_running}')
    last_task = c.get_actual_task() or c.get_latest_task()
    context = {
       'task': last_task,
        'is_running': is_running,
        'cp': c.crawler_process,
        'running_state': Task.STATE_RUNNING
    }
    if is_running:
        context = { **context, **{
            'scraped_items_number': c.get_scraped_items_number(),
            'percentage': c.get_scraped_items_percentage(),
            }

        }

    if request.is_ajax():
        #context['ajax'] = True
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
        template_name = 'task/main.html'
        return render(request, template_name, context)
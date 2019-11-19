from django.shortcuts import render
from django.http import HttpResponse
from .tasks import run_crawler, CrawlProcess

# Create your views here.
# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e


# python manage.py process_tasks
def run_crawler_view(request, *args):
    template_name = 'task/main.html'
    c = CrawlProcess.get_instance()
    if request.GET.get('crawl', None) != None:
        user = request.user
        c.start(user)
    is_running = c.is_scrapping()
    context = {
        'is_running': is_running,
    }
    if is_running:
        context = { **context, **{
            'scraped_items_number': c.get_scraped_items_number(),
            'percentage': c.get_scraped_items_percentage(),
            'init_datetime': c.get_init_datetime(),
            }
        }
    return render(request, template_name, context)
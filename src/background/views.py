from django.shortcuts import render
from django.http import HttpResponse
from .bg import process_async, ProcessExecutor, Some, Q, QueueShared, run_crawler, crawl_async, run_cp, crawl, crawl2, Crawl
import multiprocessing
from subprocess import Popen
import subprocess
import time
from multiprocessing import Process, Queue
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from ie_scrapy.spiders.ie import InfoempleoSpider
from twisted.internet import reactor
from scrapy import signals
from scrapy.signalmanager import dispatcher
# Create your views here.
# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e
# Si utilizamos una multiprocessing.Queue en al vista -> Error: Object of type Queue is not JSON serializable



# python manage.py process_tasks
def bg_task_view(request):
    print(f'{multiprocessing.current_process().name}: g_task_view')
    try:
        val = ProcessExecutor.q.get(block=False)
    except:
        val = 0
    try:
       val2 = Q.get(block=False)
    except:
        val2 = 0
    if val == 0 and val2 == 0:
        process_async()
        print('Ejecutado process async')
    return HttpResponse(f'<h1>Background task: {val}, {val2}</h1>')

# python manage.py process_tasks
def bg2(request):
    print('bg2')
    count = None
    #date_start, count, date_end = run_crawler()
    #run_cp() # -> signal only work in main thread

   

    is_running, count = crawl()



    #run_crawler()
    #return HttpResponse(f'<h1>Crawl_async</h1><p>Started at {date_start}</p><p>Items srapped: {count}</p>')
    return HttpResponse(f'<h1>Running CP</h1>{is_running, count}<p>')


def bg3(request):
    try:
        val2 = Q.get(block=False)
    except:
        val2 = 3
    Q.put(val2 + 3)

    ProcessExecutor.q.put(3)
    ProcessExecutor.q.put(4)
    print(ProcessExecutor.q.get())
    return HttpResponse(f'<h1>BG3: {Q.get(block=False)}</h1>')


#@staff_member_required
#def run_crawler(request):
def bg4(request):
    print('bg4')
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;
    #run_crawler_async()
    return HttpResponse("<h1>%Crawler running...</h1><a href='admin/'>Go to admin</a>")

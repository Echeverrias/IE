from django import db
from background_task import background
from multiprocessing import  Queue, Pipe, Process
import multiprocessing
#from billiard import Process
from datetime import datetime
from scrapy.crawler import Crawler, CrawlerProcess, CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from ie_scrapy.spiders.ie import InfoempleoSpider
from scrapy import signals
from scrapy.signalmanager import dispatcher
# from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from .models import Task
from job.models import Job
from utilities import save_error, Lock, write_in_a_file
import time
from task.models import Task
from celery import Celery, shared_task, current_app
from celery.schedules import crontab
from django.db.utils import InterfaceError
from background_task import background


app = Celery()
# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e
# https://stackabuse.com/asynchronous-tasks-in-django-with-redis-and-celery/

class CrawlProcess():

    _model = Task
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        print(CrawlProcess.__instance)
        if CrawlProcess.__instance == None:
            CrawlProcess()
        return CrawlProcess.__instance

    def __init__(self):
        if CrawlProcess.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            CrawlProcess.__instance = self
            self._id_task = None
            self.process = None
            self.q = None
            self.qitems = None
            self._count = 0
            self._items = []
            self._init_signals()


    def _init_signals(self):
        dispatcher.connect(self._spider_opened, signals.spider_opened)
        dispatcher.connect(self._item_scraped, signals.item_scraped)
        dispatcher.connect(self._spider_closed, signals.spider_closed)
        dispatcher.connect(self._engine_stopped, signals.engine_stopped)
        dispatcher.connect(self._spider_error, signals.spider_error)

    def _get_task(self, id):
        if id:
            try:
                task = Task.objects.get(id=id)
            except InterfaceError:
                db.connection.close()
                task = Task.objects.get(id=id)
            return task
        else:
            return None

    def _save_task(self, task):
        try:
            task.save()
        except InterfaceError:
            db.connection.close()
            task.save()
        return task

    def _spider_opened(self, *args, **kwargs):
        print(f'{multiprocessing.current_process().name}: *!!OPEN')

        write_in_a_file('CrawlerProcess.signal.open', {'args': args, 'kwargs': kwargs, 'process': self.process}, 'task.txt')
        self.count = 0
        try:
            t = self._get_task(self._id_task)
            t.name = str(self.process.pid)
            self._save_task(t)
        except Exception as e:
            t.name = e
            t.save()
        # q.put_nowait()
        print()


    def _spider_closed(self, spider, reason):
        print(f'{multiprocessing.current_process().name}: *!!CLOSE')
        write_in_a_file('CrawlerProcess.signal.close', {'reason': reason}, 'task.txt')
        t = self._get_task(self._id_task)
        d = datetime.today()
        t.description = f'spider closed with count: {CrawlProcess.count} at {str(d)}'
        t.result = self._count
        self._save_task(t)


    def _item_scraped(self, item, response, spider):
        print(f'{multiprocessing.current_process().name}: *!!SCRAPED')

        print()
        self._items.append(item)
        self.qitems.put(item)
        self._count = self._count + 1
        n = self._count
        write_in_a_file('CrawlerProcess.signal.scraped_item', {'response': response, 'item': item, 'count': n}, 'task.txt')
        try:
            self.q.get_nowait()
            self.q.put_nowait(n)
        except:
            self.q.put_nowait(n)

    def _engine_stopped(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.stopped', {'args': args, 'kwargs': kwargs}, 'task.txt')

    def _spider_error(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.error', {'args': args, 'kwargs': kwargs}, 'task.txt')

    def _crawl(self):
        write_in_a_file('CrawlerProcess.signal.error', {'signals': dir(signals)}, 't.txt')
        crawler = CrawlerProcess(get_project_settings())
        crawler.crawl(InfoempleoSpider)
        # To prevent the infamous error: django.db.utils.InterfaceError: (0, '')
        db.connection.close()
        crawler.start()
        write_in_a_file('CrawlProcess.start: process started', {}, 'debug.txt')
        crawler.join()
        write_in_a_file('CrawlProcess.crawl: process.join', {}, 'task.txt')
        write_in_a_file('CrawlProcess.crawl: process.join', {}, 'spider.txt')
        print('Crawler Process has Finished!!!!!')


    def _clear_queue(self):
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except:
                pass
        while not self.qitems.empty():
            try:
                self.qitems.get_nowait()
            except:
                pass


    def _init_process(self, user):
        print(f'CrawlerProcess.init_process')
        self.q = Queue()
        self.qitems = Queue()
        self.q.put_nowait(0)
        self.qresult = Queue()
        self.process = Process(target=self._crawl, args=())
        task = Task.objects.create(user=user, state=Task.STATE_PENDING, type=Task.TYPE_CRAWLER)
        self._id_task = task.pk


    def _start_process(self):
        print(f'CrawlerProcess._start_process')
        self.init_datetime = timezone.now()  # Before create the task
        self.process.start()
        task = self._get_task(self._id_task)
        task.pid = self.process.pid
        write_in_a_file('CrawlProcess._start_process: process started', {'pid': self.process.pid}, 'debug.txt')
        task.state = Task.STATE_RUNNING
        self._save_task(task)


    def _reset_process(self, state=Task.STATE_FINISHED):
        print(f'CrawlerProcess._reset_process({state})')
        try:
            self.process.terminate()
            write_in_a_file('_reset_process terminated (from stop)', {'is_running': self.process.is_alive()}, 'debug.txt')
            task = self._get_task(self._id_task)
            task.state = state
            self._save_task(task)
            self.process.join()  # ! IMPORTANT after .terminate -> .join
            try:
                task = self._get_task(self._id_task)
                task.result = self.qitems().qsize()
                self._save_task(task)
            except Exception as  e:
                print(e)
            write_in_a_file('_reset_process joinned (from stop)', {'is_running': self.process.is_alive()}, 'debug.txt')
        except Exception as e:
            print(e)
        self._clear_queue()


    def _update_process(self):
        print('CrawlerProcess._update_process')
        print(f'process is alive: {self.process and self.process.is_alive()}')
        # If the process has finished
        if self.process and not self.process.is_alive():
            self._reset_process()


    def start(self, user=None, **kwargs):
        """
        Si el proceso no está vivo es que o no se ha iniciado aún o que ya ha terminado, así que
        se guardan los datos almacenados y se ejecuta el proceso.
        Si el proceso está vivo no se hace nada.

        :param user: The uses that make the request
        :param kwargs:
        :return:
        """
        print(f'self.q.empty(): {self.q and self.q.empty()}')
        print(f'self.q.qsize(): {self.q and self.q.qsize()}')

        if not self.is_scrapping():
            task = self._get_task(self._id_task)
            if task and (task.state == Task.STATE_RUNNING): # The process has finished and we have to update the state
                self._reset_process()
            self._init_process(user)
            self._start_process()

    def stop(self):
        print(f'CrawleProcess.stop')
        self._reset_process(Task.STATE_INCOMPLETE)


    def get_actual_task(self):
        self._update_process()
        return self._get_task(self._id_task)


    def get_latest_task(self):
        last_task = Task.objects.get_latest_crawler_task()
        actual_task = self._get_task(self._id_task)
        # If the latest task from de db has state equal STATE_RUNNING and not is the actual task will be an incomplete task...
        #... and would have to update its state
        is_an_incomplete_task = (
                last_task and
                last_task.state == Task.STATE_RUNNING and
                (not actual_task or actual_task.pk != last_task.pk)
        )
        if is_an_incomplete_task:
            last_task.state = Task.STATE_INCOMPLETE
            self._save_task(last_task.id)
        return last_task


    def is_scrapping(self):
        print(CrawlProcess.is_scrapping)
        if self.process:
            return self.process.is_alive()
        else:
            return False


    def _get_scraped_jobs(self):
        latest_task = Task.objects.get_latest_crawler_task()
        if latest_task:
            tz = latest_task.created_at
            return Job.objects.registered_or_modified_after(tz)
        else:
            return Job.objects.none()


    def get_scraped_items_number(self):
        print()
        print('!!!! CrawlProcess.get_scraped_items_number');print();
        count = self._count
        try:
            print(self.q)
            #print(f'CrawlProcess.count: {CrawlProcess.count}')
            #print(f'qsize: {self.q.qsize()}')
            count = self.q.get(block=True, timeout=5)
            self._count = count
            print(f'q.count: {count}')
        except Exception as e:
            print(f'get_scraped_items_number')
           # save_error(e, {'count': count})
        #return count
        return self.qitems.qsize()


    def get_scraped_items_percentage(self):
        # Calcula el total con los items scrapeados de la tarea enterior
        count = self.get_scraped_items_number()
        task = Task.objects.get_latest_finished_crawler_task()
        scraped_jobs = Job.objects.registered_or_modified_after(self.init_datetime)
        write_in_a_file('Job.objects.registered_or_modified_after', {'scraped-jobs': scraped_jobs and scraped_jobs.count()}, 'debug.txt')
        if task:
            old_result = task.result or 20000
        else:
            old_result = 20000

        if count < old_result:
            total = old_result
        else:
            total = count

        db_count = self._get_scraped_jobs().count()

        try:
            percentage = round(db_count/total, 2)
        except:
            percentage = 0

        if  percentage >= 0.95 and self.is_scrapping():
            percentage = 0.95

        return percentage



@app.task(name="run_crawler")
def run_crawler():
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;
    write_in_a_file('run crawler start', {}, 'celery.txt')
    try:
        dispatcher.connect(lambda _: print('finish'), signal=signals.spider_closed)#'item_scraped'
        dispatcher.connect(lambda _: print('item scraped'), signal=signals.item_scraped)#'item_scraped'
        crawler_settings = get_project_settings()
        runner = CrawlerRunner(crawler_settings)
        deferred = runner.crawl(InfoempleoSpider)
        deferred.addBoth(lambda _: reactor.stop())
        print('reactor...')
        print('run!!!!!')
        reactor.run()
        write_in_a_file('run crawler end', {}, 'celery.txt')
        print('end!!!!!')
    except Exception as e:
       print(e)


@background(schedule=10)
def bg_run_crawler():
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;
    write_in_a_file('run crawler start', {}, 'bg-task.txt')
    def start():
        try:
            dispatcher.connect(lambda _: print('finish'), signal=signals.spider_closed)#'item_scraped'
            dispatcher.connect(lambda _: print('item scraped'), signal=signals.item_scraped)#'item_scraped'
            crawler_settings = get_project_settings()
            runner = CrawlerRunner(crawler_settings)
            deferred = runner.crawl(InfoempleoSpider)
            deferred.addBoth(lambda _: reactor.stop())
            print('reactor...')
            print('run!!!!!')
            reactor.run()
            write_in_a_file('run crawler end', {}, 'bg-task.txt')
            print('end!!!!!')
        except Exception as e:
           print(e)

    p = Process(target=start)
    p.start()
    print('process started')
    p.join()
    print('process joined')

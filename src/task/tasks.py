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
            self.process = None
            self._crawler_process = None
            self.task = None
            self.q = None
            self.qresult = None
            self.qitems = None
            self._count = 0
            self._items = []

    def _open(self, *args, **kwargs):
        print(f'{multiprocessing.current_process().name}: *!!OPEN')

        write_in_a_file('CrawlerProcess.signal.open', {'args': args, 'kwargs': kwargs, 'process': self.process}, 'task.txt')
        self.count = 0
        try:
            t = Task.objects.get_latest_crawler_task()
            t.name = str(self.process.pid)
            t.save()
        except Exception as e:
            t.name = e
            t.save()
        # q.put_nowait()
        print()


    def _close(self, spider, reason):
        print(f'{multiprocessing.current_process().name}: *!!CLOSE')
        write_in_a_file('CrawlerProcess.signal.close', {'reason': reason}, 'task.txt')
        t = Task.objects.get_latest_crawler_task()
        d = datetime.today()
        t.description = f'spider closed with count: {CrawlProcess.count} at {str(d)}'
        t.result = self._count
        t.save()



    def _scraped(self, item, response, spider):
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

    def _stopped(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.stopped', {'args': args, 'kwargs': kwargs}, 'task.txt')

    def _error(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.error', {'args': args, 'kwargs': kwargs}, 'task.txt')

    def _crawl(self, q):
        write_in_a_file('CrawlerProcess.signal.error', {'signals': dir(signals)}, 't.txt')
        self._crawler_process = CrawlerProcess(get_project_settings())
        self._crawler_process.crawl(InfoempleoSpider)
        dispatcher.connect(self._open, signals.spider_opened)
        dispatcher.connect(self._scraped, signals.item_scraped)
        dispatcher.connect(self._close, signals.spider_closed)
        dispatcher.connect(self._stopped, signals.engine_stopped)
        dispatcher.connect(self._error, signals.spider_error)
        """
        crawler = Crawler(InfoempleoSpider())
        self._crawler_process.crawl(crawler)
        crawler.signals.connect(self._open, signal=signals.spider_opened)
        crawler.signals.connect(self._scraped, signal=signals.item_scraped)
        crawler.signals.connect(self._close, signal=signals.spider_closed)
        crawler.signals.connect(self._stopped, signal=signals.engine_stopped)
        crawler.signals.connect(self._error, signal=signals.spider_error)
        """
        write_in_a_file('CrawlProcess.crawl: before', {'crawler_process': str(self._crawler_process)},'debug.txt')
        write_in_a_file('CrawlProcess.crawl: after', {'crawler_process': str(self._crawler_process)}, 'debug.txt')
        # To prevent the infamous error: django.db.utils.InterfaceError: (0, '')
        db.connection.close()
        self._crawler_process.start()
        write_in_a_file('CrawlProcess.start: process started', {'crawler_process': str(self._crawler_process)}, 'debug.txt')
        self._crawler_process.join()
        write_in_a_file('CrawlProcess.crawl: process.join', {}, 'task.txt')
        write_in_a_file('CrawlProcess.crawl: process.join', {}, 'spider.txt')
        print('Crawler Process has Finished!!!!!')
        q.put_nowait(self._items)


    def _clear_queue(self):
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except:
                pass
        while not self.qitems.empty():
            try:
                self.q.get_nowait()
            except:
                pass


    def _init_process(self, user):
        print(f'CrawlerProcess.init_process')
        self.q = Queue()
        self.qitems = Queue()
        self.q.put_nowait(0)
        self.qresult = Queue()
        self.process = Process(target=self._crawl, args=(self.qresult,))
        self.task = Task(user=user, state=Task.STATE_PENDING, type=Task.TYPE_CRAWLER)


    def _start_process(self):
        print(f'CrawlerProcess._start_process')
        self.init_datetime = timezone.now()  # Before create the task
        self.process.start()
        self.task.pid = self.process.pid
        write_in_a_file('CrawlProcess._start_process: process started', {'pid': self.process.pid, 'crawler_process':str(self._crawler_process)}, 'debug.txt')
        self.task.state = Task.STATE_RUNNING
        self.task.save()


    def _reset_process(self, state=Task.STATE_FINISHED):
        print(f'CrawlerProcess._reset_process({state})')
        try:
            self.process.terminate()
            write_in_a_file('_reset_process terminated (from stop)', {'is_running': self.process.is_alive()}, 'debug.txt')
            self.task.state = state
            self.task.save()
            self.process.join()  # ! IMPORTANT after .terminate -> .join
            try:
                items = self.qresult.get_nowait()
                self.task.result = len(items)
                self.task.save()
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
            if self.task and (self.task.state == Task.STATE_RUNNING):
                self._reset_process()
            self._init_process(user)
            self._start_process()

    def stop(self):
        print(f'CrawleProcess.stop')
        self._reset_process(Task.STATE_INCOMPLETE)
       # self._crawler_process.stop()
        #self._crawler_process.join()


    def get_actual_task(self):
        self._update_process()
        return self.task


    def get_latest_task(self):
        last_task = Task.objects.get_latest_crawler_task()
        # If the latest task from de db has state equal STATE_RUNNING and not is the actual task will be an incomplete task...
        #... and would have to update its state
        is_an_incomplete_task = (
                last_task and
                last_task.state == Task.STATE_RUNNING and
                (not self.task or self.task.pk != last_task.pk)
        )
        if is_an_incomplete_task:
            last_task.state = Task.STATE_INCOMPLETE
            last_task.save()
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


class CrawlerScript():

    def __init__(self):
        self.crawler = None
        self.process = None
        self.items = []

        self._count = 0


    def _so(self):
        write_in_a_file('spider_opened 1', {'open': 'open!'}, "t.txt")

    def _sc(self):
        write_in_a_file('spider_closed', {'scraped items': len(self.items)}, "t.txt")

    def _so2(self):
        write_in_a_file('spider_opened 2', {}, "t.txt")

    def _item_scraped(self, item, **kwargs):
        self._count = self._count + 1
        write_in_a_file('item scraped', {'count':self._count, 'item': item, 'kwargs':kwargs}, "t.txt")
        self.items.append(item)

    def _crawl(self, queue, spider):
        self.crawler = CrawlerProcess(get_project_settings())
        self.crawler.crawl(spider)
        write_in_a_file('CrawlerProcess.signals', {'signals': dir(signals)}, 'task.txt')
        dispatcher.connect(self._item_scraped, signals.item_scraped)
        dispatcher.connect(self._sc, signals.spider_closed)
        dispatcher.connect(self._so, signals.spider_opened)

        write_in_a_file('crawler start', {'db': dir(db), 'db.connection': dir(db.connection)}, "t.txt")
        print(dir(db.connection))
        db.connection.close()
        self.crawler.start()
        self.crawler.stop()
        write_in_a_file('crawler ended', {'qsize': queue.qsize() }, "t.txt")
        queue.put_nowait(self.items)
        write_in_a_file('crawler ended after q', {'qsize': queue.qsize()}, "t.txt")

    def crawl(self, spider):
        queue = Queue()
        self.process = Process(target=self._crawl, args=(queue, spider,))
        self.process.start()
        write_in_a_file('crawler started', {'crawler': dir(self.crawler)}, "t.txt")
        self.process.join()
        return self.process, queue
        #return queue.get(True)


def run_crawler_script():
    crawler = CrawlerScript()
    spider = InfoempleoSpider()
    p, q = crawler.crawl(spider)


def run_crawler_async():
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


#@shared_task(name='run_crawler')
@app.task(name="run_crawler")
def run_crawler():
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;
    write_in_a_file('run crawler start', {}, 'celery.txt')
    Job.objects.filter(area=Job.AREA_BANKING_AND_INSURANCE).delete()
    try:
        crawler_settings = get_project_settings()
        runner = CrawlerRunner(crawler_settings)
        dispatcher.connect(lambda _: print('finish'), signal=signals.spider_closed)#'item_scraped'
        dispatcher.connect(lambda _: print('item scraped'), signal=signals.item_scraped)#'item_scraped'
        deferred = runner.crawl(InfoempleoSpider)
        deferred.addBoth(lambda _: reactor.stop())
        print('reactor...')
        print('run!!!!!')
        reactor.run()
        write_in_a_file('run crawler end', {}, 'celery.txt')
        print('end!!!!!')
    except Exception as e:
       print(e)


#@shared_task(name='print')
@app.task(name='print_something')
def print_something():
    x = "print_something"
    write_in_a_file('print_something',{},'celery.txt')
    print(x)
    return x


@shared_task(name='print_something3')
def print_something3():
    x = "print_something3"
    write_in_a_file('print_something3',{},'celery.txt')
    print(x)
    return x

@shared_task(name='print_something4')
def print_something4():
    x = "print_something4"
    write_in_a_file('print_something4',{},'celery.txt')
    print(x)
    return x

@shared_task(name='print_something5')
def print_something5():
    x = "print_something5"
    write_in_a_file('print_something5',{},'celery.txt')
    print(x)
    return x
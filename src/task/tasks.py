from background_task import background
from multiprocessing import Process, Queue, Pipe
import multiprocessing
from datetime import datetime
from scrapy.crawler import Crawler, CrawlerProcess
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

# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e


class CrawlProcess():

    _model = Task
    __instance = None
    count = 0

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
            #self.process = Process(target=CrawlProcess.crawl)
            self.process = None
            self.crawler_process = None
            self.task = None
            self.q = Queue()
            self.parent_conn, self.child_conn = Pipe()



    #@classmethod
    #def crawl(cls, q):
    #@classmethod
    #def crawl(cls, process, q):
    @classmethod
    def crawl(cls, q, conn):
        print()
        print()
        print('***************************************************************************************')
        print('crawl')

        def close(spider, reason):
            print(f'{multiprocessing.current_process().name}: *!!CLOSE')
            write_in_a_file('CrawlerProcess.signal.close', {'reason': reason}, 'task.txt')
            t = Task.objects.get_latest_crawler_task()
            d = datetime.today()
            t.description = f'spider closed with count: {CrawlProcess.count} at {str(d)}'
            t.save()

        def open(spider):
            print(f'{multiprocessing.current_process().name}: *!!OPEN')
            try:
                name = spider.name
            except:
                name = str(spider)
            write_in_a_file('CrawlerProcess.signal.open', {'spider': name}, 'task.txt')
            CrawlProcess.count = 0
            try:
                t = Task.objects.get_latest_crawler_task()
                t.name = str(process.pid)
                t.save()
            except Exception as e:
                t.name = e
                t.save()
            #q.put_nowait()
            print()


        def scraped(item, response, spider):
            print(f'{multiprocessing.current_process().name}: *!!SCRAPED')

            print()
            CrawlProcess.count = CrawlProcess.count + 1
            n = CrawlProcess.count
            write_in_a_file('CrawlerProcess.signal.scraped_item', {'response': response, 'count': n}, 'task.txt')
            try:
                q.get_nowait()
                q.put_nowait(n)
            except:
                q.put_nowait(n)

        def stopped(*args, **kwargs):
            write_in_a_file('CrawlerProcess.signal.stopped', {'args': args, 'kwargs': kwargs}, 'task.txt')

        def error(*args, **kwargs):
            write_in_a_file('CrawlerProcess.signal.error', {'args': args, 'kwargs': kwargs}, 'task.txt')

        process = CrawlerProcess(get_project_settings())
        process.crawl(InfoempleoSpider())
        crawler = Crawler(InfoempleoSpider())
        crawler.signals.connect(open, signal=signals.spider_opened)
        crawler.signals.connect(scraped, signal=signals.item_scraped)
        crawler.signals.connect(close, signal=signals.spider_closed)
        crawler.signals.connect(stopped, signal=signals.engine_stopped)
        crawler.signals.connect(error, signal=signals.spider_error)
        time.sleep(20)
        process.crawl(crawler)
        time.sleep(20)
        process.start()
        conn.send(process)
        conn.close()
        print('***************************************************************************************')
        print(f'CrawlerProcess: {process}')
        print(dir(process))
        print('***************************************************************************************')
        print()
        print()
        write_in_a_file('CrawlProcess.crawl', {'CrawlerProcess': str(process), 'dir(CrawlerProcess)': dir(process)}, 'task.txt')
        #process.join()
        write_in_a_file('CrawlProcess.crawl: process.join', {}, 'task.txt')
        write_in_a_file('CrawlProcess.crawl: process.join', {}, 'spider.txt')

        print('Crawler Process has Finished!!!!!')



    @classmethod
    def crawl2(cls, q):
        while CrawlProcess.count < 15:
           # print(f'doing something: {CrawlProcess.count}')
            CrawlProcess.count = CrawlProcess.count + 1
            n = CrawlProcess.count
            try:
                q.get_nowait()
            except:
                pass
            q.put(n)
            if CrawlProcess.count % 5 == 0:
               # print(f'qsize: {q.qsize()}')
                time.sleep(5)


    def _clear_queue(self):
        while not self.q.empty():
            self.q.get_nowait()



    def _init_process(self, user):
        print(f'CrawlerProcess.init_process')
        self.q.put_nowait(0)
        self.process = Process(target=CrawlProcess.crawl, args=(self.q, self.child_conn,))
        self.task = Task(user=user, state=Task.STATE_PENDING, type=Task.TYPE_CRAWLER)



    def _start_process(self):
        print(f'CrawlerProcess._start_process')
        self.init_datetime = timezone.now()  # Before create the task
        self.process.start()
        self.task.pid = self.process.pid
        self.task.state = Task.STATE_RUNNING
        self.task.save()
        self.crawler_process = self.parent_conn.recv()
        write_in_a_file('CrawlProcess._start_process', {'CrawlerProcess': str(self.crawler_process), 'dir(CrawlerProcess)': dir(self.crawler_process)},'task.txt')


    def _reset_process(self, state=Task.STATE_FINISHED):
        print(f'CrawlerProcess._reset_process({state})')
        try:
            self.process.terminate()
            self.process.join()  # ! IMPORTANT after .terminate -> .join
        except:
            pass
        try:
            self.result = self.q.get_nowait()
        except Exception as e:
            pass
        self._clear_queue()
        self.task.state = state
        self.task.save()

    def _update_process(self):
        print('CrawlerProcess._update_process')
        print(f'process is alive: {self.process and self.process.is_alive()}')
        if self.process and not self.process.is_alive():
            self._reset_process()


    def start(self, user, **kwargs):
        """
        Si el proceso no está vivo es que o no se ha iniciado aún o que ya ha terminado, así que
        se guardan los datos almacenados y se ejecuta el proceso.
        Si el proceso está vivo no se hace nada.

        :param user: The uses that make the request
        :param kwargs:
        :return:
        """
        print(f'self.q.empty(): {self.q.empty()}')
        print(f'self.q.qsize(): {self.q.qsize()}')

        if not self.is_scrapping():
            if self.task and (self.task.state == Task.STATE_RUNNING):
                self._reset_process()
            self._init_process(user)
            self._start_process()

    def stop(self):
        print(f'CrawleProcess.stop')
        self.crawler_process.stop()
        self._reset_process(Task.STATE_INCOMPLETE)

    def join(self):
        self.process.join()

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
        return Job.objects.filter(Q(created_at__gte=latest_task.created_at) | Q(updated_at__gte=latest_task.created_at))

    def get_scraped_items_number(self):
        print()
        print('!!!! CrawlProcess.get_scraped_items_number');print();
        count = CrawlProcess.count
        try:
            print(self.q)
            #print(f'CrawlProcess.count: {CrawlProcess.count}')
            #print(f'qsize: {self.q.qsize()}')
            count = self.q.get(block=True, timeout=5)
            CrawlProcess.count = count
            print(f'q.count: {count}')
        except Exception as e:
            print(f'get_scraped_items_number')
            save_error(e, {'count': count})
        return count


    def get_scraped_items_percentage(self):
        # Calcula el total con los items scrapeados de la tarea enterior
        count = self.get_scraped_items_number()
        tasks = Task.objects.all().order_by('-created_at')
        if tasks and tasks.count() > 1:
            old_result = tasks[1].result
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



def run_crawler(user):
    c = CrawlProcess.get_instance()
    c.start(user)
    return c.is_scrapping(), c.get_scraped_items_number()
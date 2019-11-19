from background_task import background
from multiprocessing import Process, Queue
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

# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e

class CrawlProcess():

    q = Queue()
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
            self.init_datetime = timezone.now()
            self.process = Process(target=CrawlProcess.crawl)
            self.task = None


    def get_scraped_items_number(self):
        try:
            count = CrawlProcess.q.get_nowait()
            CrawlProcess.q.put_nowait(count)
        except:
            if count:
                count = count
            else:
                count = 0
        return count

    @classmethod
    def crawl(cls):

        def close(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!CLOSE')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');


        def open(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!OPEN')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}')
            cls.q.put_nowait()
            print()

        def idle(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!IDLE')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}')
            print()

        def scraped(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!SCRAPED')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}')
            print()
            try:
                count = cls.q.get_nowait()
                cls.q.put_nowait(count + 1)
            except:
                cls.q.put_nowait(1)

        process = CrawlerProcess(get_project_settings())
        process.crawl(InfoempleoSpider())
        crawler = Crawler(InfoempleoSpider())
        crawler.signals.connect(open, signal=signals.spider_opened)
        crawler.signals.connect(scraped, signal=signals.item_scraped)
        crawler.signals.connect(close, signal=signals.spider_closed)
        crawler.signals.connect(idle, signal=signals.spider_idle)
        process.crawl(crawler)
        process.start()

    def _clear_queue(self):
        while not CrawlProcess.q.empty():
            CrawlProcess.q.get_nowait()

    def is_scrapping(self):
        return self.process.is_alive()

    def start(self, user, **kwargs):
        """
        Si el proceso no está vivo es que o no se ha iniciado aún o que ya ha terminado, así que
        se guardan los datos almacenados y se ejecuta el proceso.
        Si el proceso está vivo no se hace nada.

        :param user: The uses that make the request
        :param kwargs:
        :return:
        """
        print(f'CrawlProcess.q.empty(): {CrawlProcess.q.empty()}')
        print(f'CrawlProcess.q.qsize(): {CrawlProcess.q.qsize()}')

        if not self.is_scrapping():
            if self.task & (self.task.state == Task.STATE_RUNNING):
                self.result = CrawlProcess.q.get_nowait()
                self.task.state = Task.STATE_FINISHED
                self.task.state.save()
            self.process.close()
            self.process = Process(target=CrawlProcess.crawl)
            self.initdatetime = timezone.now() # Before create the task
            self._clear_queue()
            CrawlProcess.q.put_nowait(0)
            self.task = Task(user=user, type=Task.TYPE_CRAWLER)
            self.task.save()
            self.process.start()

    def get_init_datetime(self):
        return self.init_datetime

    def join(self):
        self.process.join()

    def _get_scraped_jobs(self):
        return Job.objects.filter(Q(created_at__gte=self.init_datetime) or Q(updated_at__gte=self.init_datetime) )

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
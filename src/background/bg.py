from background_task import background
from multiprocessing import Process, Queue
import multiprocessing
import time
import threading

from scrapy.crawler import CrawlerRunner, CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings
from ie_scrapy.spiders.ie import InfoempleoSpider
from twisted.internet import reactor
from scrapy import signals
from scrapy.signalmanager import dispatcher
from datetime import datetime

# https://medium.com/@robinttt333/running-background-tasks-in-django-f4c1d3f6f06e

class QueueShared:

    q = Queue()

    def __init__(self):
        self.q = Queue()

    @classmethod
    def put(cls, x):
        cls.q.put(x)

    @classmethod
    def get(cls):
        return cls.q.get()

def foo(do):
    do('d')

class ProcessExecutor():

    count = 0
    q = Queue() # To communicate with django process
    init_date = None
    finish_date = None

    def __init__(self):
       # self.process = Process(target=ProcessExecutor.increment_count)
       self.process = Process(target=ProcessExecutor.run_crawler)

    @classmethod
    def run_crawler(cls):
        print('run_crawler')

        def spider_opened(**kwargs):
            print(f'{multiprocessing.current_process().name}: *qOPENED')
            #cls.q.put(datetime.today())
            cls.q.put(0)
            cls.init_date = datetime.today()
            #reactor.stop()

        def spider_closed(**kwargs):
            print(f'{multiprocessing.current_process().name}: *qCLOSED')
            #while q.size > 2:
            #    cls.q.get_nowait()
            cls.finish_date(datetime.today())
            #reactor.stop()

        def item_scraped(**kwargs):
            print(f'{multiprocessing.current_process().name}: *qSCRAPED')
            try:
                items_scraped = cls.q.get_nowait()
                cls.q.put_nowait(items_scraped + 1)
            except:
                cls.q.put_nowait(1)

        try:
            print(f'{multiprocessing.current_process().name}: run_crawler')
            crawler_settings = get_project_settings()
            runner = CrawlerRunner(crawler_settings)
            """
            dispatcher.connect(lambda _: spider_opened(_), signal=signals.spider_opened)  # 'item_scraped'
            dispatcher.connect(lambda _: spider_closed(_), signal=signals.spider_closed)  # 'item_scraped'
            dispatcher.connect(lambda _: item_scraped(_), signal=signals.item_scraped)  # 'item_scraped'
            deferred = runner.crawl(InfoempleoSpider())
            """
            crawler = Crawler(InfoempleoSpider())
            crawler.signals.connect(lambda _: spider_opened(_), signal=signals.spider_opened)  # 'item_scraped'
            crawler.signals.connect(lambda _: spider_closed(_), signal=signals.spider_closed)  # 'item_scraped'
            crawler.signals.connect(lambda _: item_scraped(_), signal=signals.item_scraped)  # 'item_scraped'
            deferred = runner.crawl(crawler)
            deferred.addBoth(lambda _: reactor.stop())
            print('reactor...')
            reactor.run()
            print('run!!!!!')


        except Exception as e:
            print(e)


    @classmethod
    def increment_count(cls):
        def plus_one():
            cls.count = cls.count + 1

        print(f'{multiprocessing.current_process().name}: incrementing count')
        for i in range(1, 1000):
            #plus_one()
            foo(lambda _: plus_one())
            cls.q.put(cls.count)
            cls.q.put(cls.count)
            cls.q.put(cls.count)
            cls.q.put(cls.count)
            print(f'{multiprocessing.current_process().name}: {cls.q.get()}')
            time.sleep(1)


    def start(self):
        print(f'{multiprocessing.current_process().name}: ProcessExecutor.start()')
        #self.process.daemon = True
        self.process.start()
        ProcessExecutor.q.put(datetime.today())
        print(f'{multiprocessing.current_process().name}: process started')

    def join(self):
        print(f'{multiprocessing.current_process().name}: ProcessExecutor.join()')
        self.process.join()
        print(f'{multiprocessing.current_process().name}: process joined')


Q = Queue()

def run_crawler():
    print(f'{multiprocessing.current_process().name}: run_crawler')

    count = None

    if ProcessExecutor.q.empty():
        process = ProcessExecutor()
        process.start()
        print(f'{multiprocessing.current_process().name}: ProcessExecutor has been created')
    else:

        try:
            """
            print(f'ProcessExecutor.q.qsize(): {ProcessExecutor.q.qsize()}')
            if ProcessExecutor.q.qsize() == 3:
                date_end = ProcessExecutor.q.get_nowait()
            elif ProcessExecutor.q.qsize() == 2:
                count = ProcessExecutor.q.get_nowait()
            date_start = ProcessExecutor.q.get_nowait()
            """
            count = ProcessExecutor.q.get_nowait()
            ProcessExecutor.q.put_nowait(count)
        except:
            pass


    return ProcessExecutor.init_date, count, ProcessExecutor.finish_date
# python manage.py process_tasks
#@background(schedule=1)
def process_async():
    print(f'{multiprocessing.current_process().name}: process_async')
    try:
        val = ProcessExecutor.q.get(block=False)
        print(f'{multiprocessing.current_process().name}: ProcessExecutor.q: {val}')
    except:
        pass
    try:
        val2 = Q.get(block=False)
        print(f'{multiprocessing.current_process().name}: Q: {val2}')
    except:
        pass
    time.sleep(5)
    process = ProcessExecutor(Q)
    process.start()
    print(f'{multiprocessing.current_process().name}: process_async started')
    process.join()
    try:
        for i in range(1, 100):
            print(Q.get())
    except:
        pass
    print(f'{multiprocessing.current_process().name}: process_async joined')


def run_crawler2(q):
    print('run_crawler')
    def close():
        q.put('close')
        print('CLOSE')

    def scraped():
        q.put('scraped')
        print('SCRAPED')

    try:
        print('run_crawler')
        crawler_settings = get_project_settings()
        runner = CrawlerRunner(crawler_settings)
        dispatcher.connect(close, signal=signals.spider_closed)#'item_scraped'
        dispatcher.connect(scraped, signal=signals.item_scraped)#'item_scraped'
        deferred = runner.crawl(InfoempleoSpider)
        deferred.addBoth(lambda _: reactor.stop())
        print('reactor...')
        q.put('reactor...')
        reactor.run()
        print('run!!!!!')
        q.put('run')
    except Exception as e:
        print(e)
        q.put(e)

#@background(schedule=1)
def run_crawler_async():
    print('run_crawler_async')
    var = None
    try:
        for i in range(1,100):
            var_ = Q.get(block=False)
            print(f'run_crawler_async q.get: {var_}')
            var = var_
    except:
        pass
    if not var:
        p = Process(target=run_crawler, args=(Q,))
        p.start()
    else:
        Q.put('running')
        var = "running..."

    return var

    print('END of run_crawler_async')

class Some():
    class Some():

        x = 0
        y = 0
        qx = Queue()

        def __init__(self):
            self.t = threading.Thread(target=Some.class_method)

        @classmethod
        def class_method(cls):
            print('class_method started')
            for i in range(1, 5):
                try:
                    cls.x = cls.x + cls.qx.get(block=False)
                except:
                    cls.x = cls.x + 1
                cls.y = cls.y + 1
                time.sleep(4)
            print('class_method ended')

        def start(self):
            self.t.start()

        def join(self):
            self.t.join()

class CrawlerScript(Process):

    Q = Queue()

    def __init__(self, spider):

        print('CrawlerScript.__init__')
        def close():
            print('CLOSE!')
            reactor.stop()

        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
       # self.crawler.signals.connect(reactor.stop, signal=signals.item_scraped)  # 'item_scraped'
       # self.crawler.signals.connect(close, signal=signals.spider_closed)
        self.spider = spider

    def run(self):
        print('run')
        self.crawler.crawl(self.spider)
        reactor.run()

def crawl_async():
    print('crawl_async')
    spider = InfoempleoSpider()
    crawler = CrawlerScript(spider)
    crawler.start()
    #crawler.join()


class CP():


    #crawler = CrawlerProcess(get_project_settings())

    def __init__(self, crawler):
        crawler_ = CrawlerProcess(get_project_settings())
        self._add_signals(crawler)
        crawler_.crawl(crawler)
        self.process = Process(target=crawler_.start)

    def _add_signals(self, crawler):

        def close(*args, **kwargs):
            print('*CLOSE')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');print()

        def open(*args, **kwargs):
            print('*OPEN')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');
            print()

        def scraped(*args, **kwargs):
            print('*SCRAPED')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');
            print()

        #dispatcher.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        #dispatcher.connect(close, signal=signals.spider_closed)  # 'item_scraped'
        #dispatcher.connect(scraped, signal=signals.item_scraped)  # 'item_scraped'  dispatcher.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        crawler.signals.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        crawler.signals.connect(scraped, signal=signals.item_scraped)  # 'item_scraped'
        crawler.signals.connect(close, signal=signals.spider_closed)  # 'item_scraped'



    def start(self):
        print('* CP.start')
        self.process.start(stop_after_crawl=False)

    def join(self):
        print('* CP.start')
        self.process.start(stop_after_crawl=False)


def run_cp():
    print('run_cp')
    crawler = Crawler(InfoempleoSpider())
    cp = CP(crawler)
    cp.start()


def crawl2():

    def crawl_():

        def close(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!CLOSE')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');
            print()

        def open(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!OPEN')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');
            print()

        def scraped(*args, **kwargs):
            print(f'{multiprocessing.current_process().name}: *!!SCRAPED')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}');
            print()

        process = CrawlerProcess(get_project_settings())


        dispatcher.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        dispatcher.connect(close, signal=signals.spider_closed)  # 'item_scraped'
        dispatcher.connect(scraped, signal=signals.item_scraped)  # 'item_scraped'  dispatcher.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        process.crawl(InfoempleoSpider())

        """
        crawler = Crawler(InfoempleoSpider())
        crawler.signals.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        crawler.signals.connect(scraped, signal=signals.item_scraped)  # 'item_scraped'
        crawler.signals.connect(close, signal=signals.spider_closed)  # 'item_scraped'
        process.crawl(crawler)
        """
        process.start()

    p = Process(target=crawl_)
    p.start()


class Crawl():

    q = Queue()
    __instance = None
    state = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        print(Crawl.__instance)
        if Crawl.__instance == None:
            Crawl()
        return Crawl.__instance

    def __init__(self):
        if Crawl.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Crawl.__instance = self
            self.process = Process(target=Crawl.crawl)


    def get_scraped_items_number(self):
        try:
            count = Crawl.q.get_nowait()
            Crawl.q.put_nowait(count)
        except:
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
        """
        dispatcher.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        dispatcher.connect(close, signal=signals.spider_closed)  # 'item_scraped'
        dispatcher.connect(scraped, signal=signals.item_scraped)  # 'item_scraped'  dispatcher.connect(open, signal=signals.spider_opened)  # 'item_scraped'
       
        """
        crawler = Crawler(InfoempleoSpider())
        crawler.signals.connect(open, signal=signals.spider_opened)  # 'item_scraped'
        crawler.signals.connect(scraped, signal=signals.item_scraped)  # 'item_scraped'
        crawler.signals.connect(close, signal=signals.spider_closed)  # 'item_scraped'
        crawler.signals.connect(idle, signal=signals.spider_idle)  # 'item_scraped'
        process.crawl(crawler)

        process.start()

    def _clear_queue(self):
        while not Crawl.q.empty():
            Crawl.q.get_nowait()


    def is_scrapping(self):
        return self.process.is_alive()

    def start(self):
        print(f'Crawl.q.empty(): {Crawl.q.empty()}')
        print(f'Crawl.q.qsize(): {Crawl.q.qsize()}')


        if not self.is_scrapping():
            self.process.close()
            self.process = Process(target=Crawl.crawl)
            self._clear_queue()
            self.process.start()
            Crawl.q.put_nowait(0)


    def join(self):
        self.process.join()




def crawl():
    c = Crawl.getInstance()
    c.start()
    return c.is_scrapping(), c.get_scraped_items_number()
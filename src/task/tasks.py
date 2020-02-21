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
from utilities import save_error, write_in_a_file
import time
from task.models import Task
from celery import Celery, shared_task, current_app
from celery.schedules import crontab
from django.db.utils import InterfaceError
from background_task import background
import os, signal



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
            self.qis_scrapping = None
            self._count = 0
            self._items = []
            self._is_resetting = False
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
            except Exception as e: #InterfaceError:
                print(f'_get_task -> Error: {e}')
                db.connection.close()
                task = Task.objects.get(id=id)
                print(f'_get_task -> task.id: {task.id}')
            return task
        else:
            return None

    def _save_task(self, task):
        try:
            task.save()
        except Exception as e:  # InterfaceError:
            print(f'_get_task -> Error: {e}')
            task.save()
        return task

    def _spider_opened(self, *args, **kwargs):
        print(f'{multiprocessing.current_process().name}: *!!OPEN')

        write_in_a_file('CrawlerProcess.signal.open', {'args': args, 'kwargs': kwargs, 'process': self.process}, 'task.txt')
        self._count = 0
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
        print(f'{multiprocessing.current_process().name}: *!!CLOSING SPIDER')
        write_in_a_file('CrawlerProcess.signal.close', {'reason': reason}, 'task.txt')
        t = self._get_task(self._id_task)
        d = datetime.today()
        t.description = f'spider closed with count: {self._count} at {str(d)}'
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
        except:
            pass
        finally:
            self.q.put(n)

    def _engine_stopped(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.stopped', {'args': args, 'kwargs': kwargs}, 'task.txt')

    def _spider_error(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.error', {'args': args, 'kwargs': kwargs}, 'task.txt')

    def _empty_queue(self, q):
        write_in_a_file(f'CrawlProcess._clear_queque:', {}, 'tasks.txt')
        print(f'CrawlProcess._clear_queque:')
        while True:
            try:
                self.q.get(block=False)
            except Exception as e:
                print(f'CrawlProcess._clear_queque - Error: {e}')
                print(f'CrawlProcess._clear_queque - queue.qsize: {q.qsize()}')
                write_in_a_file(f'CrawlProcess._clear_queque: error - {e}', {}, 'tasks.txt')
                write_in_a_file(f'CrawlProcess._clear_queque: error - queue.qsize: {q.qsize()}', {}, 'tasks.txt')
                break
        print(f'CrawlProcess._clear_queque: queue empty?')
        write_in_a_file(f'CrawlProcess._clear_queque: queue empty?', {}, 'tasks.txt')


    def _close_queue(self, q):
        print(f'CrawlProcess._close_queque:')
        try:
            write_in_a_file(f'CrawlProcess._clear_queque: close...', {}, 'tasks.txt')
            q.close()
            q.join_thread()
            write_in_a_file(f'CrawlProcess._clear_queque: queue closed', {}, 'tasks.txt')
        except Exception as e:
            print(f'CrawlProcess._close_queque - Error: {e}')
            write_in_a_file(f'CrawlProcess._clear_queque: close -> {e}', {}, 'tasks.txt')


    def _empty_and_close_queue(self, q):
        self._empty_queue(q)
        self._close_queue(q)

    def _crawl(self, qis_running):
        write_in_a_file('CrawlerProcess.signal.error', {'signals': dir(signals)}, 't.txt')
        qis_running.put('running')
        crawler = CrawlerProcess(get_project_settings())
        crawler.crawl(InfoempleoSpider)
        # To prevent the infamous error: django.db.utils.InterfaceError: (0, '')
        db.connection.close()
        crawler.start()
        write_in_a_file('CrawlProcess.start: process started', {}, 'debug.txt')
        crawler.join()
        write_in_a_file('CrawlProcess.crawl: process joined', {}, 'task.txt')
        write_in_a_file('CrawlProcess.crawl: process joined', {}, 'tasks.txt')
        write_in_a_file('CrawlProcess.crawl: process joined', {}, 'spider.txt')
        print('Crawler Process has Finished!!!!!')
        write_in_a_file(f'Crawler Process - before: qis_running.qsize: {qis_running.qsize()}', {}, 'tasks.txt')
        try:
            qis_running.get()
        except Exception as e:
            write_in_a_file(f'Crawler Process - error in qis_running.get: {e}', {}, 'tasks.txt')
        write_in_a_file(f'Crawler Process - after: qis_running.qsize: {qis_running.qsize()}', {}, 'tasks.txt')
        write_in_a_file('===========================================================================================', {}, 'tasks.txt')
        print();print()


    def _empty_and_close_queues(self):
        write_in_a_file(f'CrawlProcess._clear_queques: q', {}, 'tasks.txt')
        self._empty_and_close_queue(self.q)
        write_in_a_file(f'CrawlProcess._clear_queques: qitems', {}, 'tasks.txt')
        self._empty_and_close_queue(self.qitems)
        write_in_a_file(f'CrawlProcess._clear_queques: qis_scrapping', {}, 'tasks.txt')
        self._empty_and_close_queue(self.qis_scrapping)
        write_in_a_file(f'CrawlProcess._clear_queques: all queues have been celaned', {}, 'tasks.txt')



    def _init_process(self, user):
        print(f'CrawlerProcess.init_process')
        self.q = Queue()
        self.qitems = Queue()
        # If qis_scrapping has size > 0 this means the process is scrapping
        self.qis_scrapping = Queue()
        self.q.put(0)
        self.qresult = Queue()
        self.process = Process(target=self._crawl, args=(self.qis_scrapping,))
        task = Task.objects.create(user=user, state=Task.STATE_PENDING, type=Task.TYPE_CRAWLER)
        self._id_task = task.pk


    def _start_process(self):
        print(f'CrawlerProcess._start_process')
        self.init_datetime = timezone.now()  # Before create the task
        self.process.start()
        task = self._get_task(self._id_task)
        task.pid = self.process.pid
        write_in_a_file('CrawlProcess._start_process: process started', {'pid': self.process.pid}, 'tasks.txt')
        task.state = Task.STATE_RUNNING
        self._save_task(task)


    def _reset_process(self, state=Task.STATE_FINISHED):
        self._is_resetting = True
        print(f'CrawlerProcess._reset_process({state})')
        number_of_processed_items  = self.qitems.qsize()
        try:


            self._empty_and_close_queues()
            print("CrawlerProcess._reset_process - queues closed")
            self.process.terminate()
            print('._reset_process 1')
            write_in_a_file('_reset_process terminated (from stop)', {'is_running': self.process.is_alive()}, 'tasks.txt')

            task = self._get_task(self._id_task)
            print('._reset_process 2')
            task.state = state
            self._save_task(task)
            print('._reset_process 3')
            write_in_a_file('_reset_process before join (from stop)', {},'tasks.txt')
            self.process.join(120)  # ! IMPORTANT after .terminate -> .join
            try:
                os.kill(self.process.pid, signal.SIGTERM)
            except Exception as e:
                print(f'_reset_process - Error trying to kill the process {self.process.pip}: {e}')
                write_in_a_file(f'_reset_process - Error trying to kill the process {self.process.pip}', {}, 'tasks.txt')
                pass
            write_in_a_file('_reset_process after join (from stop)', {}, 'tasks.txt')
            try:
                task = self._get_task(self._id_task)
                print('._reset_process 4')
                task.result = number_of_processed_items
                self._save_task(task)
                print('._reset_process 5')
            except Exception as  e:
                print(e)
            write_in_a_file('_reset_process joinned (from stop)', {'is_running': self.process.is_alive()}, 'tasks.txt')
        except Exception as e:
            print(e)
        finally:
            self.process = None
            self._is_resetting = False

        self._count = 0


    def _update_process(self):
        print(f'CrawlerProcess._update_process -> is_resetting: {self._is_resetting}')
        print(f'process is alive: {self.process and self.process.is_alive()}')
        write_in_a_file(f'__update_process - process == {self.process.is_alive() if self.process else None}', {}, 'tasks.txt')
        # If the process has finished
        try:
            if not self.process.is_alive() and not self._is_resetting:
                self._reset_process()
        except:
            pass


    def start(self, user=None, **kwargs):
        """
        Si el proceso no está vivo es que o no se ha iniciado aún o que ya ha terminado, así que
        se guardan los datos almacenados y se ejecuta el proceso.
        Si el proceso está vivo no se hace nada.

        :param user: The uses that make the request
        :param kwargs:
        :return:
        """
        print(f'self.q.qsize(): {self.q and self.q.qsize()}')

        if not self.is_scrapping():
            task = self._get_task(self._id_task)
            if task and (task.state == Task.STATE_RUNNING) and (not self._is_resetting): # The process has finished and we have to update the state
                self._reset_process()
            self._init_process(user)
            self._start_process()

    def _stop(self, state=Task.STATE_INCOMPLETE):
        print(f'CrawleProcess.stop -> is_resetting: {self._is_resetting}')
        if not self._is_resetting:
            self._reset_process(state)



    def get_actual_task(self):
        print(f'CrawleProcess.get_actual_task')
        self._update_process()
        return self._get_task(self._id_task)


    def get_latest_task(self):
        print("get_latest_task")
        last_task = Task.objects.get_latest_crawler_task()
        print(f"last_task: {last_task}")
        actual_task = self._get_task(self._id_task)
        print(f"actual_task: {actual_task}")
        # If the latest task from de db has state equal STATE_RUNNING and not is the actual task will be an incomplete task...
        #... and would have to update its state
        is_an_incomplete_task = (
                last_task and
                last_task.state == Task.STATE_RUNNING and
                (not actual_task or (actual_task.pk != last_task.pk))
        )
        if is_an_incomplete_task:
            print('last_task is an incomplete task')
            last_task.state = Task.STATE_INCOMPLETE
            self._save_task(last_task)
        return last_task


    def is_scrapping(self):
        print('CrawlProcess.is_scrapping')
        # ñapa
        if self.qis_scrapping and self.process:
            __d = {'qis_scrapping.qsize': self.qis_scrapping.qsize(), 'process.is_alive': self.process.is_alive()}
        else:
            __d = {}
        write_in_a_file(f'CrawlProcess.is_scrapping', __d, 'tasks.txt')
        print(f'is_scraping - {__d}')
        if self.process:
            write_in_a_file(f'is_scraping - process != None', __d,'tasks.txt')
            print(f'CrawlProcess.is_scrapping - process.is_alive?:{self.process.is_alive()}')
            if self.qis_scrapping.qsize() > 0:
                write_in_a_file(f'is_scraping - there is something in qis_scrapping ({self.qis_scrapping.qsize()}) -> True - process.is_alive -> {self.process.is_alive()}', {}, 'tasks.txt')
                # return self.process.is_alive()
                return True
            else:
                write_in_a_file(f'is_scraping - there is nothing in qis_scrapping -> False', __d, 'tasks.txt')
                print('The process is scrapping no more')
                self._stop(state=Task.STATE_FINISHED)
                return False
        else:
            write_in_a_file('is_scraping - process == None -> False', {}, 'tasks.txt')
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
        print('!!!! CrawlProcess.get_scraped_items_number');print()
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
        # return count
        # return self.qitems.qsize()
        return self._count




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


@background(schedule=1)
def prueba2():
    time.sleep(10)


@background(schedule=5)
def bg_run_crawler():
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;
    #### ÑAPA ##########
    print();print('bg_run_crawler')
    Job.objects.filter(state=Job.AREA_LEGAL).delete()
    print(os.getcwd())
    try:
        os.remove('parsed urls state.json')
        #os.remove('bg-task.txt')
    except: pass
    ####################

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
            print('end!!!!!')
        except Exception as e:
           print(e)

    p = Process(target=start)
    p.start()
    print();
    print(f'run crawler start at {str(datetime.now())}');
    print()
    write_in_a_file(f'run crawler start at {str(datetime.now())}', {}, 'bg-task.txt')
    p.join()
    print();
    print(f'run crawler end at {str(datetime.now())}');
    print()
    write_in_a_file(f'run crawler end at {str(datetime.now())}', {}, 'bg-task.txt')
    print('process joined')


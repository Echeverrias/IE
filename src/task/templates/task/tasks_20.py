import django
django.setup()
from django import db
from django.utils import timezone
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from multiprocessing import  Queue, Process
from datetime import datetime
import os, signal
from .models import Task
from job.models import Job
from utilities.utilities import save_error, write_in_a_file

class SpiderProcess():

    _model = Task
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        print(SpiderProcess.__instance)
        if SpiderProcess.__instance == None:
            SpiderProcess()
        return SpiderProcess.__instance

    def __init__(self):
        if SpiderProcess.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SpiderProcess.__instance = self
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
                db.connection.close()
                task = Task.objects.get(id=id)
            return task
        else:
            return None

    def _update_task(self, id, data):
        if id:
            try:
                data['updated_at'] = timezone.localtime(timezone.now())
                Task.objects.filter(id=id).update(**data)
                task = Task.objects.get(id=id)
            except Exception as e: #InterfaceError:
                db.connection.close()
                Task.objects.filter(id=id).update(**data)
                task = Task.objects.get(id=id)
            return task
        else:
            return None

    def _spider_opened(self, *args, **kwargs):
        write_in_a_file('CrawlerProcess.signal.open', {'args': args, 'kwargs': kwargs, 'process': self.process}, 'task.txt')
        self._count = 0
        # q.put_nowait()

    def _spider_closed(self, spider, reason):
        write_in_a_file('CrawlerProcess.signal.close', {'reason': reason}, 'task.txt')
        now = datetime.now()
        data = {
            'description': f'spider closed with count: {self._count} at {str(now)}',
            'result': self._count,
            'finished_at': now
        }
        self._update_task(self._id_task, data)

    def _item_scraped(self, item, response, spider):
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
        write_in_a_file(f'SpiderProcess._clear_queque:', {}, 'tasks.txt')
        while True:
            try:
                self.q.get(block=False)
            except Exception as e:
                write_in_a_file(f'SpiderProcess._clear_queque: error - {e}', {}, 'tasks.txt')
                write_in_a_file(f'SpiderProcess._clear_queque: error - queue.qsize: {q.qsize()}', {}, 'tasks.txt')
                break
        write_in_a_file(f'SpiderProcess._clear_queque: queue empty?', {}, 'tasks.txt')

    def _close_queue(self, q):
        try:
            write_in_a_file(f'SpiderProcess._clear_queque: close...', {}, 'tasks.txt')
            q.close()
            q.join_thread()
            write_in_a_file(f'SpiderProcess._clear_queque: queue closed', {}, 'tasks.txt')
        except Exception as e:
            write_in_a_file(f'SpiderProcess._clear_queque: close -> {e}', {}, 'tasks.txt')

    def _empty_and_close_queue(self, q):
        self._empty_queue(q)
        self._close_queue(q)

    def _crawl(self, spider, qis_running):
        write_in_a_file('CrawlerProcess.signal.error', {'signals': dir(signals)}, 't.txt')
        qis_running.put(spider)
        crawler = CrawlerProcess(get_project_settings())
        crawler.crawl(spider)
        # To prevent the infamous error: django.db.utils.InterfaceError: (0, '')
        db.connection.close()
        crawler.start()
        write_in_a_file('SpiderProcess.start: process started', {}, 'debug.txt')
        crawler.join()
        write_in_a_file('SpiderProcess.crawl: process joined', {}, 'task.txt')
        write_in_a_file('SpiderProcess.crawl: process joined', {}, 'tasks.txt')
        write_in_a_file('SpiderProcess.crawl: process joined', {}, 'spider.txt')
        write_in_a_file(f'Crawler Process - before: qis_running.qsize: {qis_running.qsize()}', {}, 'tasks.txt')
        while True:
            try:
                qis_running.get(block=False)
            except Exception as e:
                write_in_a_file(f'Crawler Process - error in qis_running.get: {e}', {}, 'tasks.txt')
                break
        write_in_a_file(f'Crawler Process - after: qis_running.qsize: {qis_running.qsize()}', {}, 'tasks.txt')
        write_in_a_file('===========================================================================================', {}, 'tasks.txt')

    def _empty_and_close_queues(self):
        write_in_a_file(f'SpiderProcess._clear_queques: q', {}, 'tasks.txt')
        self._empty_and_close_queue(self.q)
        write_in_a_file(f'SpiderProcess._clear_queques: qitems', {}, 'tasks.txt')
        self._empty_and_close_queue(self.qitems)
        write_in_a_file(f'SpiderProcess._clear_queques: qis_scrapping', {}, 'tasks.txt')
        self._empty_and_close_queue(self.qis_scrapping)
        write_in_a_file(f'SpiderProcess._clear_queques: all queues have been celaned', {}, 'tasks.txt')

    def _init_process(self, spider, user):
        """
        Creates a process to run the spider and create-persist a Task instance

        :param spider: Spider
        :param user: User
        :return: None
        """
        self.q = Queue()
        self.qitems = Queue()
        # If qis_scrapping has size > 0 this means the process is scrapping
        self.qis_scrapping = Queue()
        self.q.put(0)
        self.qresult = Queue()
        self.process = Process(target=self._crawl, args=(spider, self.qis_scrapping,))
        task = Task.objects.create(user=user, name=spider.name, state=Task.STATE_PENDING, type=Task.TYPE_CRAWLER)
        self._id_task = task.pk

    def _start_process(self):
        """
        Starts the process and update the Task instance with the pid process and the running state

        :return: None
        """
        self.init_datetime = timezone.now()  # Before create the task
        self.qis_scrapping.put('YES')
        self.process.start()
        write_in_a_file('SpiderProcess._start_process: process started', {'pid': self.process.pid}, 'tasks.txt')
        data = {
            'pid': self.process.pid,
            'state': Task.STATE_RUNNING,
            'started_at': datetime.now(),
        }
        self._update_task(self._id_task, data)

    def _reset_process(self, state=Task.STATE_FINISHED):
        self._is_resetting = True
        number_of_processed_items  = self.qitems.qsize()
        try:
            self._empty_and_close_queues()
            self.process.terminate()
            write_in_a_file('_reset_process terminated (from stop)', {'is_running': self.process.is_alive()}, 'tasks.txt')
            data = {
                'state': state,
                'result': number_of_processed_items,
                'finished_at': datetime.now(),
            }
            self._update_task(self._id_task, data)
            write_in_a_file('_reset_process before join (from stop)', {},'tasks.txt')
            self.process.join(120)  # ! IMPORTANT after .terminate -> .join
            try:
                os.kill(self.process.pid, signal.SIGTERM)
            except Exception as e:
                write_in_a_file(f'_reset_process - Error trying to kill the process {self.process.pip}', {}, 'tasks.txt')
                pass
            write_in_a_file('_reset_process after join (from stop)', {}, 'tasks.txt')
            write_in_a_file('_reset_process joinned (from stop)', {'is_running': self.process.is_alive()}, 'tasks.txt')
        except Exception as e:
            pass
        finally:
            self.process = None
            self._id_task = None
            self._is_resetting = False
        self._count = 0

    def _update_process(self):
        """
        The process is reset if it is not alive and if it has'nt being reset
        """
        write_in_a_file(f'__update_process - process == {self.process.is_alive() if self.process else None}', {}, 'tasks.txt')
        # If the process has finished
        try:
            if not self.process.is_alive() and not self._is_resetting:
                self._reset_process()
        except:
            pass

    def start(self, spider, user=None, **kwargs):
        """
        Si el proceso no está vivo es que o no se ha iniciado aún o que ya ha terminado, así que
        se guardan los datos almacenados y se ejecuta el proceso.
        Si el proceso está vivo no se hace nada.

        :param user: The uses that make the request
        :param kwargs:
        :return:
        """
        if not self.is_scrapping():
            task = self._get_task(self._id_task)
            if task and (task.state == Task.STATE_RUNNING) and (not self._is_resetting): # The process has finished and we have to update the state
                self._reset_process()
            self._init_process(spider, user)
            self._start_process()

    def _stop(self, state=Task.STATE_INCOMPLETE):
        if not self._is_resetting:
            self._reset_process(state)

    def get_actual_task(self):
        self._update_process()
        return self._get_task(self._id_task)

    def _update_last_db_task_if_is_incomplete(self, last_db_task, actual_task):
        """
         If the latest task from de db has state equal STATE_RUNNING and not is the actual task...
         ... will be an incomplete task and would have to update its state
        """
        is_an_incomplete_task = (
                last_db_task and
                last_db_task.state == Task.STATE_RUNNING and
                (not actual_task or (actual_task.pk != last_db_task.pk))
        )
        if is_an_incomplete_task:
            id = last_db_task.id
            data = {'state': Task.STATE_INCOMPLETE}
            last_db_task = self._update_task(id, data)
        return last_db_task

    def get_latest_task(self):
        last_task = Task.objects.get_latest_crawler_task()
        actual_task = self._get_task(self._id_task)
        return self._update_last_db_task_if_is_incomplete(last_task, actual_task)

    def get_latest_tasks(self):
        last_tasks = Task.objects.get_latest_crawler_tasks()
        actual_task = self._get_task(self._id_task)
        return [self._update_last_db_task_if_is_incomplete(last_task, actual_task) for last_task in last_tasks]

    def is_scrapping(self):
        # ñapa
        if self.qis_scrapping and self.process:
            __d = {'qis_scrapping.qsize': self.qis_scrapping.qsize(), 'process.is_alive': self.process.is_alive()}
        else:
            __d = {}
        write_in_a_file(f'SpiderProcess.is_scrapping', __d, 'tasks.txt')
        print(f'is_scraping - {__d}')
        if self.process:
            write_in_a_file(f'is_scraping - process != None', __d,'tasks.txt')
            if self.qis_scrapping.qsize() > 0:
                write_in_a_file(f'is_scraping - there is something in qis_scrapping ({self.qis_scrapping.qsize()}) -> True - process.is_alive -> {self.process.is_alive()}', {}, 'tasks.txt')
                # return self.process.is_alive()
                return True
            else:
                write_in_a_file(f'is_scraping - there is nothing in qis_scrapping -> False', __d, 'tasks.txt')
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
        count = self._count
        try:
            count = self.q.get(block=True, timeout=5)
            self._count = count
        except Exception as e:
            pass
        # return count
        # return self.qitems.qsize()
        return self._count
import django
django.setup()
from django import db
from django.utils import timezone
from django.db.utils import InterfaceError
from scrapy import signals
from scrapy.signalmanager import dispatcher
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from multiprocessing import  Queue, Process
import logging
import os, signal
from .models import Task
from job.models import Job
import time

logging.getLogger().setLevel(logging.INFO)

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
            self._process = None
            self._qitems_number = None # Stores the number of scraped items
            self._qis_scraping = None   # If qis_scraping has size > 0 this means the process is scraping
            self._count = 0
            self._is_resetting = False
            self._init_signals()

    @property
    def process(self):
        return self._process

    def _init_signals(self):
        dispatcher.connect(self._spider_opened, signals.spider_opened)
        dispatcher.connect(self._item_scraped, signals.item_scraped)
        dispatcher.connect(self._spider_closed, signals.spider_closed)
        dispatcher.connect(self._engine_stopped, signals.engine_stopped)
        dispatcher.connect(self._spider_error, signals.spider_error)

    def get_actual_task(self):
        id = self._id_task
        if id:
            try:
                task = Task.objects.get(id=id)
            except InterfaceError:
                db.connection.close()
                task = Task.objects.get(id=id)
            except Exception:
                logging.exception(f'There should be a task in the database with id {id}')
                task = None
            return task
        else:
            return None

    def _update_task(self, id, data):
        if id:
            try:
                data['updated_at'] = timezone.localtime(timezone.now())
                Task.objects.filter(id=id).update(**data)
                task = Task.objects.get(id=id)
            except InterfaceError:
                db.connection.close()
                Task.objects.filter(id=id).update(**data)
                task = Task.objects.get(id=id)
            except Exception:
                logging.exception(f'There should be a task in the database with id {id}')
                task = None
            return task
        else:
            return None

    def _spider_opened(self, *args, **kwargs):
        logging.info("The spider is opened")
        self._count = 0

    def _spider_closed(self, spider, reason):
        logging.info("The spider is closed")
        now = timezone.localtime(timezone.now())
        data = {
            'description': f'spider closed with count: {self._count} at {str(now)}',
            'result': self._count,
            'finished_at': now
        }
        self._update_task(self._id_task, data)

    def _item_scraped(self, item, response, spider):
        self._count = self._count + 1
        n = self._count
        try:
            self._qitems_number.get_nowait()
        except:
            pass
        finally:
            self._qitems_number.put(n)

    def _engine_stopped(self, *args, **kwargs):
        logging.warn("The engine has stopped")

    def _spider_error(self, *args, **kwargs):
        logging.error(f"Some error in the spider: {args}")

    def _empty_queue(self, q):
        time.sleep(1)
        while True:
            try:
                q.get(block=False)
            except Exception:
                break

    def _close_queue(self, q):
        try:
            q.close()
            q.join_thread()
        except Exception:
            pass

    def _empty_and_close_queue(self, q):
        self._empty_queue(q)
        self._close_queue(q)

    def _execute_crawler_process(self, spider):
        crawler = CrawlerProcess(get_project_settings())
        crawler.crawl(spider)
        # To prevent the infamous error: django.db.utils.InterfaceError: (0, '')
        db.connection.close()
        crawler.start()
        logging.info("The crawler process has started")
        crawler.join()

    def _crawl(self, spider, qis_running):
        qis_running.put(spider)
        self._execute_crawler_process(spider)
        while True:
            try:
                qis_running.get(block=False)
            except Exception:
                break
        now = timezone.localtime(timezone.now())
        data = {
            'state': Task.STATE_FINISHED,
            'description': f'CrawlerProcess finished at {str(now)}',
            'result': self._count if self._count >0 else None,
            'finished_at': now
        }
        self._update_task(self._id_task, data)

    def _empty_and_close_queues(self):
        self._empty_and_close_queue(self._qitems_number)
        self._empty_and_close_queue(self._qis_scraping)

    def _init_process(self, spider, user):
        """
        Creates a process to run the spider and create-persist a Task instance

        :param spider: Spider
        :param user: User
        :return: None
        """
        self._qitems_number = Queue()
        self._qis_scraping = Queue()
        self._qitems_number.put(0)
        self._process = Process(target=self._crawl, args=(spider, self._qis_scraping,))
        task = Task.objects.create(user=user, name=spider.name, state=Task.STATE_PENDING, type=Task.TYPE_CRAWLER)
        self._id_task = task.pk


    def _start_process(self):
        """
        Starts the process and update the Task instance with the pid process and the running state

        :return: None
        """
        self.init_datetime = timezone.localtime(timezone.now())  # Before create the task
        self._qis_scraping.put('YES')
        self._process.start()
        data = {
            'pid': self._process.pid,
            'state': Task.STATE_RUNNING,
            'started_at': self.init_datetime,
        }
        self._update_task(self._id_task, data)

    def _reset_process(self):
        self._is_resetting = True
        try:
            self._empty_and_close_queues()
            self._process.terminate()
            self._process.join(120)  # ! IMPORTANT after .terminate -> .join
            try:
                pass
                os.kill(self._process.pid, signal.SIGTERM)
            except Exception:
                logging.info(f"The process {self._process.pid} is not alive")
        except Exception as e:
            logging.exception("Error in _reset_process")
        finally:
            self._process = None
            self._id_task = None
            self._is_resetting = False
        self._count = 0

    def start(self, spider, user=None, **kwargs):
        """
        Si el proceso no está vivo es que o no se ha iniciado aún o que ya ha terminado, así que
        se guardan los datos almacenados y se ejecuta el proceso.
        Si el proceso está vivo no se hace nada.

        :param user: The uses that make the request
        :param kwargs:
        :return:
        """
        if not self.is_scraping():
            task = self.get_actual_task()
            if task and (task.state == Task.STATE_RUNNING) and (not self._is_resetting):
                # The process has finished and we have to update the state
                self._stop()
            self._init_process(spider, user)
            self._start_process()

    def _stop(self, state=Task.STATE_INCOMPLETE):
        if not self._is_resetting:
            now = timezone.localtime(timezone.now())
            data = {
                'state': state,
                'description': f'process stopped at {str(now)}',
                'result': self._count if self._count > 0 else None,
                'finished_at': now
            }
            self._update_task(self._id_task, data)
            self._reset_process(state)

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
        actual_task = self.get_actual_task()
        return self._update_last_db_task_if_is_incomplete(last_task, actual_task)

    def get_latest_tasks(self):
        last_tasks = Task.objects.get_latest_crawler_tasks()
        actual_task = self.get_actual_task()
        return [self._update_last_db_task_if_is_incomplete(last_task, actual_task) for last_task in last_tasks]

    def is_scraping(self):
        if self._process:
            if self._qis_scraping.qsize() > 0:
                return True
            else:
                if not self._is_resetting:
                    self._reset_process()
                return False
        else:
            return False

    def get_scraped_items_number(self):
        try:
            count = self._qitems_number.get(block=True, timeout=5)
            self._count = count
        except Exception:
            pass
        return self._count
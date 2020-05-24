from task.tasks import SpiderProcess
from task.models import Task
from multiprocessing import Process, Queue
import time

class FakeSpiderProcess(SpiderProcess):

    __instance = None
    _sp = SpiderProcess.get_instance()

    @staticmethod
    def get_instance():
        """ Static access method. """
        if FakeSpiderProcess.__instance == None:
            FakeSpiderProcess()
        return FakeSpiderProcess.__instance

    def __init__(self):
        if FakeSpiderProcess.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            FakeSpiderProcess.__instance = self
            self._id_task = None
            self._process = None
            self._q = None
            self._qitems = None
            self._qis_scraping = None
            self._count = 0
            self._items = []
            self._is_resetting = False

    def _execute_crawler_process(self, spider=None):
        print('Hola')
        pass#time.sleep()

    def tearDown(self):
        Task.objects.filter(name='fake').delete()
        self._id_task = None
        self._process = None
        self._q = None
        self._qis_scraping = None
        self._count = 0
        self._is_resetting = False
        FakeSpiderProcess._sp._id_task = None
        FakeSpiderProcess._sp._process = None
        FakeSpiderProcess._sp._q = None
        FakeSpiderProcess._sp._qis_scraping = None
        FakeSpiderProcess._sp._count = 0
        FakeSpiderProcess._sp._is_resetting = False

    def simulate_running_process(self):
        task = Task.objects.create(pid=555, name='fake', state=Task.STATE_RUNNING, type=Task.TYPE_CRAWLER)
        self._id_task = task.pk
        FakeSpiderProcess._sp._id_task = task.pk
        self._process = Process()
        FakeSpiderProcess._sp._process = Process()
        q_items = Queue()
        scraped_items_number = 20
        q_items.put(scraped_items_number)
        self._q = q_items
        FakeSpiderProcess._sp._q = q_items
        qis_scraping = Queue()
        qis_scraping.put(True)
        self._qis_scraping = qis_scraping
        FakeSpiderProcess._sp._qis_scraping = qis_scraping
        return {'task': task, 'scraped_items_number': scraped_items_number}

    def simulate_finished_process(self):
        task = Task.objects.create(pid=555, name='fake', state=Task.STATE_FINISHED, result=120, type=Task.TYPE_CRAWLER)
        self._q = Queue()
        FakeSpiderProcess._sp._q = Queue()
        self._qis_scraping = Queue()
        FakeSpiderProcess._sp._qis_scraping = Queue()
        return {'task': task}


from scrapy.crawler import Crawler, CrawlerRunner, CrawlerProcess
from scrapy import signals
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from multiprocessing import Process
from .spiders import InfoempleoSpider
from scrapy.signalmanager import dispatcher

class CrawlerExecutor():

    count = 0


    def __init__(self, spider):
        def increment_count(cls):
            print('incrementing count')
            cls.count = cls.count + 1
        dispatcher.connect(lambda _: print('FINIsh'), signal=signals.spider_closed)
        dispatcher.connect(increment_count, signal=signals.item_passed)
        settings = get_project_settings()
        self.process = CrawlerProcess(settings)

        self.spider = spider

    def start(self):
        self.process.crawl(self.spider)
        self.process.start()

    def join(self):
        self.process.join()

def crawl_async():
    spider = InfoempleoSpider()
    crawler = CrawlerExecutor(spider)
    crawler.start()
    crawler.join()
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
# from billiard import Process #????????????''
from multiprocessing import Process
from .spiders import InfoempleoSpider

class CrawlerExecutor(Process):

    count = 0



    def __init__(self, spider):
        def increment_count(cls):
            print('incrementing count')
            cls.count = cls.count + 1
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(spider.__class__, settings)
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.crawler.signals.connect(increment_count, signal=signals.item_scraped)
        self.spider = spider



    def run(self):
        self.crawler.crawl(self.spider)
        reactor.run()

def crawl_async():
    spider = InfoempleoSpider()
    crawler = CrawlerExecutor(spider)
    crawler.start()
    crawler.join()
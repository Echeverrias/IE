# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html


from scrapy import signals
from scrapy.http import HtmlResponse
import random
import re
import os
import time
from time import time as now
import json
import math
from collections import namedtuple
import lxml.etree
import lxml.html
import requests
from .state_ import UrlsState
from .chrome_browser import ChromeBrowser
from .items import JobItem
from selenium.webdriver import ActionChains
from utilities import write_in_a_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('SCRAPY.MIDDLEWARES: %s'%BASE_DIR)



class IeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    JOB_URL_PATH = 'https://www.infoempleo.com/ofertasdetrabajo/'
    job_requests_count = 0
    job_requests_count2 = 0
    START = now()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        # Signals: https://docs.scrapy.org/en/latest/topics/signals.html
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(s.item_scraped, signal=signals.item_scraped)
        return s


    def item_scraped(self, response, item, spider, signal, sender) :

        print('-------------------------------------------------------------------------------------------')
        self.job_requests_count2 += 1
        write_in_a_file('IeSpiderMiddleware.item_scraped', {'response': response, 'count': self.job_requests_count, 'count2': self.job_requests_count2}, 'spider.txt')
        print('IeSpiderMiddleware.item_scraped')
        print('-------------------------------------------------------------------------------------------')

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        write_in_a_file('IeSpiderMiddleware.process_spider_input', {'response': response}, 'spider.txt')

        url = response.url

        if IeSpiderMiddleware.JOB_URL_PATH in url:
            print();print()
            print("######################################################################")
            print("#@ IeSpiderMiddleware.process_spider_input: {}".format(response.url))
            print("######################################################################")

            #print(f'job_requests_count: {self.job_requests_count}')
            UrlsState.update_url_state(response.meta[UrlsState.KEY_START_URL], response.meta[UrlsState.KEY_TOTAL_RESULTS])

        # Should return None or raise an exception.
        print("#######IeSpiderMiddleware.process_spider_input############################################");
        print();print()
        return None


    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        print();print()
        print("######################################################################")
        print("#@ IeSpiderMiddleware.process_spider_output: {}".format(response.url))
        print("######################################################################")
        print(f'response.meta: {response.meta}')
        print(response.meta)

        print("result: {}".format(result))
        print(f'job_requests_count: {self.job_requests_count}')

        for i in result:
            print();
            print('-----------------------------------------------------')
            print('RESULT:')
            print(f'type: {type(i)}')
            if type(i) == JobItem:
                self.job_requests_count += 1
                UrlsState.update_url_state(response.meta[UrlsState.KEY_START_URL], response.meta[UrlsState.KEY_TOTAL_RESULTS])
            print(f'{i}')
            print('-----------------------------------------------------');print()
            print(f'job_requests_count: {self.job_requests_count}')

            yield i
        write_in_a_file('IeSpiderMiddleware.process_spider_output', {'response': response, 'result': result, 'count': self.job_requests_count, 'count2': self.job_requests_count2}, 'spider.txt')
        print("#######IeSpiderMiddleware.process_spider_output############################################");print();print()

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        write_in_a_file('IeSpiderMiddleware.process_start_requests', {} ,'spider.txt')
        print('# ###process_start_requests')


        for r in start_requests:
            # The init url is changed for the url with the pending page query
            start_url = r.url
            r._set_url(UrlsState.get_pending_page_url(r.url))
            print(r.url)
            #print(UrlsState.get_url_data(start_url, UrlsState.KEY_RESULTS_PARSED))
            write_in_a_file('IeSpiderMiddleware.process_start_requests', {'req': r} ,'spider.txt')
            print('###end process_start_requests')
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider.Middleware opened: %s' % spider.name)
        write_in_a_file('IeSpiderMiddleware.spider_opened', {},'spider.txt')
        UrlsState.init()
        #print(UrlsState.parsed_urls)
        print('##########################################################################################')


        spider.logger.info('Spider.Middleware opened: %s' % 'end')

    def spider_closed(self, spider):
        spider.logger.info('Spider.Middleware closed: %s', spider.name)
        write_in_a_file('IeSpiderMiddleware.spider_closed', {}, 'spider.txt')
        UrlsState.close()
        print(f'job_requests_count: {self.job_requests_count}')
        print(f'job_requests_count2: {self.job_requests_count2}')
        print(f'time: {IeSpiderMiddleware.START - now()}')



class IeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    JOB_RESULTS_URL_PATHS = [
        'https://www.infoempleo.com/ofertas-internacionales/',
        'https://www.infoempleo.com/trabajo/',
        'https://www.infoempleo.com/primer-empleo/',
    ]

    def __get_chrome_browser(self, request=None):
        if request:
            try:
                ua = str(request.headers['User-Agent'])
            except Exception as e:
                print(e)
            try:
                proxy = request.meta['proxy']
            except Exception as e:
                print(e)
        else:
            ua = ChromeBrowser.get_user_agent()
            proxy = ChromeBrowser.get_proxy()
        return ChromeBrowser.get_driver(proxy=proxy, user_agent=ua)


    def __init__(self):
        print('IeSpiderDownloaderMiddleware.init')
        self.driver = None



    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(s.item_scraped, signal=signals.item_scraped)
        return s

    def item_scraped(self, *args, **kwargs):
        write_in_a_file('IeSpiderDownloaderMiddleware.item_scraped', {}, 'spider.txt')

        print('-------------------------------------------------------------------------------------------')
        print('IeSpiderDownloaderMiddleware.item_scraped')
        print(f'args: {args}')
        print(f'kwargs: {kwargs}')

        print('-------------------------------------------------------------------------------------------')

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        write_in_a_file('IeSpiderDownloaderMiddleware.process_request', {'request': request}, 'spider.txt')
        print(f'IeSpiderDownloaderMiddleware.process_request: {request.url}')
        try:
            print(request.meta[UrlsState.KEY_START_URL])
        except:
            print('error: request.meta')
        try:
            print(request['meta'][UrlsState.KEY_START_URL])
        except:
            print('error: request[meta]')
        # The request.url must be:
        # - a job url
        # - a job results page url
        url = request.url
        url_to_parse = request.url
        print('url: %s'%url)
        print('url_to_parse: %s' %url_to_parse)
        if not self.__is_a_valid_job_results_url(url):
            print('#This url will not process by selenium: %s' % url)
            return None
        else:
            print('IM SELENIUM PROCESSING THE REQUEST: %s' % request.url)  ##
            if not self.driver:
                self.driver = self.__get_chrome_browser(request)

        clean_url = self.__clean_url(url)
        print('clean url: %s' % clean_url)

        if self.__is_first_request(clean_url):
            print('Selenium is going to get the clean url %s for first time' % (url))
            self.__create_a_new_tab(url)
        else:
            self.__select_tab(clean_url)

        self.__do_something_random()
        body = self.driver.page_source
        return HtmlResponse(url_to_parse, body=body, encoding='utf-8', request=request)



    def __is_first_request(self, url):
        print('#_is_first_request')
        ##state = UrlsState.get_parsed_url_state(url)
        if UrlsState.exist_url_state(url):
            return UrlsState.get_url_data(url, UrlsState.KEY_IS_FIRST_REQUEST)
        else:
            UrlsState._create_parsed_url_state(url)
            return True


    def __select_tab(self, url):
        self.driver.switch_to.window(self.driver.window_handles[UrlsState.get_index_tab(url)])


    def __create_a_new_tab(self, url):
        ##new_index_tab = UrlsState.get_a_new_index_tab()
        print('# IESpiderDownloadMiddelwarecreated a new tab')
        ##self.parsed_urls[url]['tab'] = new_index_tab
        UrlsState.set_new_index_tab(url)
        index_tab = UrlsState.get_index_tab(url)
        if index_tab != 0:
            self.driver.execute_script("window.open('');")
            self.__select_tab(url)
        self.driver.get(url)
        UrlsState.set_url_data(url, UrlsState.KEY_IS_FIRST_REQUEST, False)


    def __do_something_random(self):
        print('#do_something_random')
        self.driver.execute_script("window.scrollBy(0, %i);"%random.randint(10, 150))
        if random.randint(0, 3) == 3:
            time.sleep(random.randint(1, 3))
            self.driver.execute_script("window.scrollBy(0, %i);" % random.randint(15, 130))


    def __go_to_the_page(self, page):
        print('#__go_to_the_page: %i' % (page))
        self.driver.execute_script("verPagina(%s);" % str(page))


    def __is_a_valid_job_results_url(self, url):
        if self.get_clean_job_url_path(url):
            return True
        else:
            return False

    def get_clean_job_url_path(self, url):
        try:
            expected_urls = '|'.join(IeDownloaderMiddleware.JOB_RESULTS_URL_PATHS)
            href_list = re.findall(expected_urls, url)
            return href_list[0]
        except:
            return None

    def __clean_url(self, url):
        page_path = re.findall('\d+/*', url)
        if page_path:
            url = url.replace(page_path[0], '')
        return url

    def process_response(self, request, response, spider):
        write_in_a_file('IeSpiderDownloaderMiddleware.process_response', {'request': request, 'response': response}, 'spider.txt')
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        write_in_a_file('IeSpiderDownloaderMiddleware.spider_openes', {}, 'spider.txt')
        spider.logger.info('Spider opened: %s' % spider.name)


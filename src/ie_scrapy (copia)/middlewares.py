# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy import signals
from scrapy.http import HtmlResponse
import random
import re
import os

#from ea.proxies import ProxiesMaker

#PROX = ProxiesMaker()

class IeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

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
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class IeSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __get_chrome_options(self, config={'proxy':None, 'user_agent':None}):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        chrome_options.add_argument("incognito")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-infobars")
        prefs = {'profile.managed_default_content_settings.images': 2} # selenium will not load the images
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--start-maximized")
        if config['user_agent']:
            print('USER AGENT: %s' % config['user_agent'])
            chrome_options.add_argument("user-agent=" + config['user_agent'])
        if config['proxy']:
            chrome_options.add_argument('--proxy-server=%s' % config['proxy'])
        return chrome_options

    def __get_chrome_browser(self, request=None):
        print('set_chrome_Browser') ##
        print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))##
        options = {'proxy': None, 'user_agent': None}
        if request:
            try:
                options['user_agent'] = str(request.headers['User-Agent'])
            except Exception as e:
                print(e)
                user_agents = ['Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) ',
                               "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)"]
                options['user_agent'] = user_agents(random.randint(0, len(user_agents) - 1))
            try:
                options['proxy'] = request.meta['proxy']
            except Exception as e:
                print(e)
        chrome_options = self.__get_chrome_options(options)
        driver = webdriver.Chrome('chromedriver', options=chrome_options)
        return driver

    def __init__(self):
        print('IeSpiderDownloaderMiddleware.init')
        self.driver = None
        self.valid_urls = ['https://www.infoempleo.com/ofertas-internacionales/',
                      "https://www.infoempleo.com/trabajo/"]

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        print('IM SELENIUM PROCESSING THE REQUEST: %s' % request.url) ##
        if not self.driver:
            self.driver = self.__get_chrome_browser(request)
        url = request.url
        page = self.__get_number_page_from_the_url(url)
        if not self.__is_a_valid_url(request.url):
            print('This url will not process by selenium: %s' % url)
            return None
        elif page == 0:
            print('Selenium is going to get the page: %s' % url)
            self.driver.get(url)
        else:
            print('Selenium is going to execute the page: %s' % url)
            self.driver.execute_script("verPagina(%s);" % str(page))
        print(page)##
        print('---')##
        body = self.driver.page_source
        return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)

    def __get_number_page_from_the_url(self, url):
        try:
            page = int(re.findall(r'\d+', url)[0])
        except:
            page = 0
        return page

    def __is_a_valid_url(self, url):
        try:
            url_list = re.findall(self.valid_urls[0] + '|' + self.valid_urls[1], url)
            return len(url_list) > 0
        except:
            return False

    def process_response(self, request, response, spider):
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
        spider.logger.info('Spider opened: %s' % spider.name)

# -*- coding: utf-8 -*-

"""
Copia con errores suponiendo que la navegación entre las paǵinas de lso resultados se hace mediante click
o ejecutando una función js en lugar de solicitando la página mediante query en la url

"""


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
import json
import math
from collections import namedtuple
import lxml.etree
import lxml.html
import requests
from src.ie_scrapy.state_ import UrlsState
from src.ie_scrapy.chrome_browser import ChromeBrowser
from selenium.webdriver import ActionChains

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('SCRAPY.MIDDLEWARES: %s'%BASE_DIR)



class IeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    JOBS_URL_PATH = "'https://www.infoempleo.com/ofertasdetrabajo/'"

    # https://docs.scrapy.org/en/latest/topics/signals.html
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s


    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        print("#IeSpiderMiddleware.process_spider_input: {}".format(response.url))
        url = response.url
        if IeSpiderMiddleware.JOBS_URL_PATH in url:
            UrlsState.update_url_state(response.meta[UrlsState.KEY_START_URL], response.meta[UrlsState.KEY_TOTAL_RESULTS])
        elif '?page=0' in url:
            print('# page not found')
            try:
                print(response.meta[UrlsState.KEY_START_URL])
            except Exception as e:
                print(f'Error!!! {e}')
            UrlsState.reset_url_state(response.meta[UrlsState.KEY_START_URL])
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        print("IeSpiderMiddleware.process_spider_output: {}".format(response.url))
        # Must return an iterable of Request, dict or Item objects.
        try:
            print(response.meta[UrlsState.KEY_START_URL])
        except:
            print(1)
        try:
            print(response['meta'][UrlsState.KEY_START_URL])
        except:
            print(2)
        print("result: {}".format(result))
        for i in result:
            print(i)
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
        print('# ###process_start_requests')


        for r in start_requests:
            # The init url is changed for the url with the pending page query
            r._set_url(UrlsState.get_pending_url(r.url))
            print(r)
            print('end')
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        UrlsState.init()
        print(UrlsState.parsed_urls)
        print('##########################################################################################')

    def spider_closed(self, spider):
        spider.logger.info('y Spider closed: %s', spider.name)
        UrlsState.close()



class IeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    JOB_RESULTS_URL_PATHS = [
        'https://www.infoempleo.com/ofertas-internacionales/',
        "https://www.infoempleo.com/trabajo/",
        "https://www.infoempleo.com/primer-empleo/",
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
        self.state = UrlState()
        self.parsed_urls = self.__get_parsed_urls_state()



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


        # The request.url must be:
        # - a job url
        # - a job results page url
        url = request.url
        url_to_parse = request.url
        print('url: %s'%url)
        print('url_to_parse: %s' %url_to_parse)
        if not self.__is_a_valid_job_results_url(url):
            print('#This url will not process by selenium: %s' % url)
            try:
                print(request)
                try:
                    print(request.meta)
                    print(request.meta[UrlsState.KEY_START_URL])
                except:
                    print('1')
                clean_url = self.__clean_url(request.meta[UrlsState.KEY_START_URL])
                print('#parsing job from: %s'%clean_url)
                ## self.__update_parsed_url(clean_url)
                print()
                print()
                print('# request.meta: %s'%request.meta[UrlsState.KEY_START_URL])
                print()
                print()
            except:
                pass
            return None
        else:
            print('IM SELENIUM PROCESSING THE REQUEST: %s' % request.url)  ##
            if not self.driver:
                self.driver = self.__get_chrome_browser(request)

        clean_url = self.__clean_url(url)
        page = self.__get_number_page_from_the_url(url)
        print('clean url: %s' % clean_url)
        print('page: %i' % page)

        try:
            if self.__is_first_request(clean_url):
                print('Selenium is going to get the page %i of %s for first time' % (page,url))
                self.__create_a_new_tab(url)
                if page == 0:
                    page = UrlsState.get_pending_page(clean_url)
                if page > 1 and page < 500:
                    self.__go_to_the_page(page)
                    url_to_parse = '%s%s/'%(clean_url, str(page))
                elif page >= 500:
                    self.__go_to_the_page(499)
                    next_page = 500
                    while next_page <= page:
                        actual_page = self._get_actual_page_from_driver()
                        print('actual_page: %i, next_page: %i'%(actual_page, next_page))
                        if actual_page and ((actual_page + 1) == next_page):
                            self.__go_to_the_next_page(next_page)
                            next_page += 1
                        else:
                            print('#something wrong')
                            break
            else:
                print('Selenium is going to get the next page %i of %s' % (page,url))
                if page == 0:
                    inexistent_page = UrlsState.get_pending_page(clean_url) + 555
                    UrlsState.reset_url_state(url)
                    print('# Im selenium, all the pages have been parsed')
                    self.__go_to_the_page(inexistent_page)
                else:
                    self.__select_tab(clean_url)
                    actual_page = self._get_actual_page_from_driver()
                    print('#actual_page: %i'%actual_page)
                    if actual_page and ((actual_page + 1) == page):
                        self.__go_to_the_next_page(page)
                    else:
                        self.__reboot_tab(clean_url, page)
        except Exception as e:
            print('#Exception __go_to_the_page: %s %i'%(clean_url,page))
            print('#Exception raised: %s'%e)
            self.__reboot_tab(clean_url, page)


        body = self.driver.page_source
        return HtmlResponse(url_to_parse, body=body, encoding='utf-8', request=request)

    def _get_actual_page_from_driver(self):
        try:
            actual_page_xpath = "//button[contains(@title, 'Página actual')]"
            actual_page = int(self.driver.find_elements_by_xpath(actual_page_xpath)[0].text)
        except Exception as e:
            actual_page = None
            print('#Error getting the actual page: %s'%e)
        return actual_page
    
    """##
    def __update_parsed_url(self, url, reset_results=False):
        if reset_results:
            #self.parsed_urls[url]['results'] = 0
            UrlsState.reset_url_state(url)
        else:
            UrlsState.update_url_state(url)
        print('# count: %i'%UrlsState.get_url_data(url, UrlsState.KEY_RESULTS_PARSED))
        #self.__save_parsed_urls_state(self.parsed_urls)
    """

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

    def __reboot_tab(self, href, page):
        print('REBOOT_TAB')
        self.driver.get(href)
        self.__go_to_the_page(page)



    def __create_a_new_tab(self, url):
        ##new_index_tab = UrlsState.get_a_new_index_tab()
        ##print('#created the tab %i'%new_index_tab)
        ##self.parsed_urls[url]['tab'] = new_index_tab
        UrlsState.set_new_index_tab(url)
        index_tab = UrlsState.get_index_tab(url)
        if index_tab != 0:
            self.driver.execute_script("window.open('');")
            self.__select_tab(url)
        self.driver.get(url)
        self.parsed_urls[url]['is_first_request'] = False



    def __go_to_the_next_page(self, page):
        print('#__go_to_the_next_page: %i'%(page))
        self.__do_something_random()
        if page == 0:
            page = 2
        return self.__click_on_the_next_page(page)


    def __do_something_random(self):
        print('#do_something_random')
        self.driver.execute_script("window.scrollBy(0, %i);"%random.randint(10, 150))
        if random.randint(0, 3) == 3:
            time.sleep(random.randint(1, 3))
            self.driver.execute_script("window.scrollBy(0, %i);" % random.randint(15, 130))


    def __click_on_the_next_page(self, page):
        try:
            print('#click_on_the_next_page: %i'%page)
            next_page_xpath = "//button[contains(@title, 'Ver página %i')]" % page
            next_page = self.driver.find_elements_by_xpath(next_page_xpath)[0]
            ActionChains(self.driver).move_to_element(next_page).perform()
            self.driver.execute_script("window.scrollBy(0, %i);" %100)
            time.sleep(random.randint(1, 3))
            ActionChains(self.driver).click(next_page).perform()
        except Exception as e:
            print('#Error when click on the page %i: %s'%(page, e))
            self.__go_to_the_page(page)


    def __go_to_the_page(self, page):
        print('#__go_to_the_page: %i' % (page))
        self.driver.execute_script("verPagina(%s);" % str(page))


    def __get_number_page_from_the_url(self, url):
        try:
            page = int(re.findall(r'\d+', url)[0])
        except:
            page = 0
        return page

    """##
    def __get_number_page_from_parsed_url_state(self, url):
        try:
            results_parsed = self.parsed_urls[url]['results']
            return int(results_parsed/20) + 1
        except:
            return 0
    """


    def __is_a_valid_job_results_url(self, url):
        if self.get_clean_job_url_path(url):
            return True
        else:
            return False

    def get_clean_job_url_path(self, url):
        try:
            expected_urls = ""
            for i, url in IeDownloaderMiddleware.JOB_RESULTS_URL_PATHS:
                expected_urls += url
                if i < len(IeDownloaderMiddleware.JOB_RESULTS_URL_PATHS):
                    expected_urls += '|'
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


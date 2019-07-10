# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from scrapy import signals
from scrapy.http import HtmlResponse
import random
import re
import os
import time
import json


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('SCRAPY.MIDDLEWARES: %s'%BASE_DIR)

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


class IeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __get_chrome_options(self, config={'proxy':None, 'user_agent':None}):
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("headless")
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
                #options['proxy'] = '153.232.171.254:8080'
            except Exception as e:
                print(e)
        chrome_options = self.__get_chrome_options(options)
        driver = webdriver.Chrome('./chromedriver', options=chrome_options)
        return driver

    def __init__(self):
        print('IeSpiderDownloaderMiddleware.init')
        self.driver = None
        self.valid_hrefs = ['https://www.infoempleo.com/ofertas-internacionales/',
                      "https://www.infoempleo.com/trabajo/",
                    "https://www.infoempleo.com/primer-empleo/"]
        self.parsed_urls = self.__get_parsed_urls_state()

    def __save_parsed_urls_state(self, data_dict):
        with open('parsed urls state.json', 'w') as fw:
            print('#saving_parsed_urls_state')
            print(data_dict)
            fw.write(json.dumps(data_dict))


    def __load_parsed_urls_state(self):
        try:
            with open('parsed urls state.json', 'r') as fr:
                return json.loads(fr.read())
        except:
            return None

    def __get_parsed_urls_state(self):
        parsed_urls = self.__load_parsed_urls_state()
        if parsed_urls:
            for url in parsed_urls.keys():
                parsed_urls[url]['is_first_request'] = True
                parsed_urls[url]['tab'] = -1
        else:
            parsed_urls = {}
        return parsed_urls

    def __create_parsed_url_state(self, url):
        print('create_parsed_url_state: %s'%url)
        state = {'is_first_request': True,
                'tab': -1,
                'results': 0
            }
        self.parsed_urls.setdefault(url, state)
        print(self.parsed_urls)

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

        url = request.url
        url_to_parse = request.url
        print('url: %s'%url)
        print('url_to_parse: %s' %url_to_parse)
        if not self.__is_a_valid_url(url):
            print('#This url will not process by selenium: %s' % url)
            try:
                print(request)
                try:
                    print(request.meta)
                    print(request.meta['results_url'])
                except:
                    print('1')
                clean_url = self.__clean_url(request.meta['results_url'])
                print('#parsing job from: %s'%clean_url)
                self.__update_parsed_url(clean_url)
                print()
                print()
                print('# request.meta: %s'%request.meta['results_url'])
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
                    page = self.__get_number_page_from_parsed_url_state(clean_url)
                if page > 1 and page < 500:
                    self.__go_to_the_page(page)
                    url_to_parse = '%s%s/'%(clean_url, str(page))
                elif page >= 500:
                    self.__go_to_the_page(499)
                    next_page = 500
                    while next_page <= page:
                        actual_page = self._get_actual_page()
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
                    end_page = self.__get_number_page_from_parsed_url_state(clean_url) + 100
                    self.__update_parsed_url(clean_url, reset_results=True)
                    print('# Im selenium, all the pages have been parsed')
                    self.__go_to_the_page(end_page)
                else:
                    self.__select_tab(clean_url)
                    actual_page = self._get_actual_page()
                    print('#actual_page: %i'%actual_page)
                    if actual_page and ((actual_page + 1) == page):
                        self.__go_to_the_next_page(page)
                    else:
                        self.__reboot_tab(clean_url, page)
        except Exception as e:
            print('#Exception __go_to_the_page: %s %i'%(clean_url,page))
            print('#Exception raised: %s'%e)
            self.__reboot_tab(clean_url, page)




        """
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.element_located_to_be_selected((By.XPATH, "//p[contains(text(),'Mostrando')]")))
        except Exception as e:
            print('Error waiting for mostrando %s' % e)
            error = True
        
        try:
             body = self.driver.page_source
             #print(body)
        except Exception as e:
            print('Error in page_source %s' % e)
            error = True
        if error:
            self.driver.quit()
            self.driver = None
        """
        body = self.driver.page_source
        return HtmlResponse(url_to_parse, body=body, encoding='utf-8', request=request)

    def _get_actual_page(self):
        try:
            actual_page_xpath = "//button[contains(@title, 'Página actual')]"
            actual_page = int(self.driver.find_elements_by_xpath(actual_page_xpath)[0].text)
        except Exception as e:
            actual_page = None
            print('#Error getting the actual page: %s'%e)
        return actual_page

    def __update_parsed_url(self, url, reset_results=False):
        if reset_results:
            self.parsed_urls[url]['results'] = 0
        else:
            self.parsed_urls[url]['results'] += 1
        print('# count: %i'%self.parsed_urls[url]['results'])
        self.__save_parsed_urls_state(self.parsed_urls)


    def __is_first_request(self, url):
        print('#_is_first_request')
        print(self.parsed_urls)
        state = self.parsed_urls.get(url, None)
        if state:
            return state['is_first_request']
        else:
            self.__create_parsed_url_state(url)
            return True


    def __select_tab(self, url):
        self.driver.switch_to.window(self.driver.window_handles[self.parsed_urls[url]['tab']])

    def __reboot_tab(self, href, page):
        print('REBOOT_TAB')
        self.driver.get(href)
        self.__go_to_the_page(page)

    def __get_a_new_index_tab(self):
        indexes_tabs = [i['tab'] for i in self.parsed_urls.values()]
        max_index_tab = max(indexes_tabs)
        return max_index_tab + 1

    def __create_a_new_tab(self, url):
        new_index_tab = self.__get_a_new_index_tab()
        print('#created the tab %i'%new_index_tab)
        self.parsed_urls[url]['tab'] = new_index_tab
        if self.parsed_urls[url]['tab'] != 0:
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

    def __get_number_page_from_parsed_url_state(self, url):
        try:
            results_parsed = self.parsed_urls[url]['results']
            return int(results_parsed/20) + 1
        except:
            return 0

    def __is_a_valid_url(self, url):
        if self.__get_href(url):
            return True
        else:
            return False

    def __get_href(self, url):
        try:
            href_list = re.findall(self.valid_hrefs[0] + '|' + self.valid_hrefs[1] + '|' + self.valid_hrefs[2], url)
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


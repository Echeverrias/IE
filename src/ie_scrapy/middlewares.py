# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Request
from scrapy.http import HtmlResponse #%
from scrapy.exceptions import IgnoreRequest
from django.utils import timezone
import os
import time
import random
from time import time as now
from dateutil.relativedelta import relativedelta
from .keys import START_URL, TOTAL_RESULTS
from utilities.utilities import write_in_a_file
from job.models import Job
from utilities.utilities import write_in_a_file


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print('SCRAPY.MIDDLEWARES: %s'%BASE_DIR)



class IeSpiderMiddleware_(object):
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
        print('IeSpiderMiddleware.item_scraped')
        self.job_requests_count2 += 1
        write_in_a_file('IeSpiderMiddleware.item_scraped', {'response': response, 'count': self.job_requests_count, 'count2': self.job_requests_count2}, 'spider.txt')
        print('IeSpiderMiddleware.process_spider_item_scraped');time.sleep(10)
        print('-------------------------------------------------------------------------------------------')

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        #"""

        print();print()
        print("########################################################################")
        print("#@ IeSpiderMiddleware.process_spider_input: {}".format(response.url))
        print("######################################################################")
        write_in_a_file('IeSpiderMiddleware.process_spider_input', {'response': response}, 'spider.txt')
        print('IeSpiderMiddleware.process_spider_input');time.sleep(10)
        print("#######IeSpiderMiddleware.process_spider_input############################################");
        print();print()
        # Should return None or raise an exception.
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
            #"""
            print();
            print('-----------------------------------------------------')
            print('RESULT:')
            print(f'type: {type(i)}')
            if type(i) == JobItem:
                self.job_requests_count += 1
            print(f'{i}')
            print('-----------------------------------------------------');print()
            print(f'job_requests_count: {self.job_requests_count}')
            print('IeSpiderMiddleware.process_spider_output & yield i');time.sleep(10)
            yield i
            print('IeSpiderMiddleware.process_spider_output  yield i ...');time.sleep(10)
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
            #start_url = r.url
            #r._set_url(start_url)
            print(r.url)
            #print(UrlsState.get_url_data(start_url, RESULTS_PARSED))
            write_in_a_file('IeSpiderMiddleware.process_start_requests', {'req': r} ,'spider.txt')
            print('###end process_start_requests')
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider.Middleware opened: %s' % spider.name)
        #"""
        write_in_a_file('IeSpiderMiddleware.spider_opened', {},'spider.txt')
        print('##########################################################################################')


        spider.logger.info('Spider.Middleware opened: %s' % 'end')

    def spider_closed(self, spider):
        spider.logger.info('Spider.Middleware closed: %s', spider.name)
        #"""
        write_in_a_file('IeSpiderMiddleware.spider_closed', {}, 'spider.txt')
        print(f'job_requests_count: {self.job_requests_count}')
        print(f'job_requests_count2: {self.job_requests_count2}')
        print(f'time: {IeSpiderMiddleware.START - now()}')



class IeDownloaderMiddleware_(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.





    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        #crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)

        return s

    def item_scraped(self, *args, **kwargs):
        write_in_a_file('IeSpiderDownloaderMiddleware.item_scraped', {}, 'spider.txt')
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
        #body = self.driver.page_source
        #return HtmlResponse(request.url, body=body, encoding='utf-8', request=request)
        return None




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
        write_in_a_file('IeSpiderDownloaderMiddleware.spider_opened', {}, 'spider.txt')
        spider.logger.info('Spider opened: %s' % spider.name)

    def spider_closed(self, spider):
        write_in_a_file('IeSpiderDownloaderMiddleware.spider_closed', {}, 'spider.txt')
        spider.logger.info('Spider closed: %s' % spider.name)


class CheckDownloaderMiddleware(object):

   def process_request(self, request, spider):
        url = request.url
        if 'ofertasdetrabajo'in url:
            ref = int(os.path.basename(os.path.dirname(url)))
            try:
                job = Job.objects.get(id=ref)
            except:
                return None
            print('**CheckDownloaderMiddleware')
            print(job.checked_at.date())
            print(timezone.localtime(timezone.now()).date())
            print(job.checked_at.date() == timezone.localtime(timezone.now()).date())
            if (job.checked_at.date() == timezone.localtime(timezone.now()).date() or
                job.checked_at.date() == timezone.localtime(timezone.now()).date() - relativedelta(days=1)
            ):
                print(f'* {url} checked today')
                print('')
                print('')
                print('IGNOREREQUEST')
                print('')
                request.meta.update({'ignore': True})
                print(request.meta)
                raise IgnoreRequest(f'Ignore request: {request.url}')
            else:
                return None
        elif not 'www.infoempleo.com' in url:
            print(f'* Ignored request to {url}')
            request.meta.update({'ignore': True})
            raise IgnoreRequest(request.url)
        else:
            return None


class PUADownloaderMiddleware(object):
    
    proxy = None
    ua = None

    def process_request(self, request, spider):
        if PUADownloaderMiddleware.proxy:# and request.meta.get('retry'):
            request.meta.update({'proxy_source': PUADownloaderMiddleware.proxy})
            request.meta.update({'proxy':
                                f'{PUADownloaderMiddleware.proxy.type}://{PUADownloaderMiddleware.proxy.host}:{PUADownloaderMiddleware.proxy.port}'})
            request.headers.update({b'User-Agent':[PUADownloaderMiddleware.ua]})


class ERDownloaderMiddleware(object):

    def _print_data(self, request, title="INFO", exception=None):
        print(f'&&&&&&&&&&&&&  {title} &&&&&&&&&&&&&&&&&')
        print('meta:')
        print(request.meta);
        print('')
        print('headers:')
        print(request.headers);
        print('')
        print('proxy:')
        print(request.meta.get('proxy'));
        print('')
        print('ua:')
        print(request.headers.get(b'User-Agent'));
        print('')
        print('')
        return {
            'description': f'{title}',
            'exception': exception,
            'url': request.url,
            'request': request,
            'meta': request.meta,
            'headers': request.headers,
            'proxy': request.meta.get('proxy'),
            'ua': request.headers.get(b'User-Agent'),
        }

    def _make_the_request_again(self, request):
        n = 100
        if request.meta.get('retry', 0) < n:
            retry = request.meta['retry'] + 1 if request.meta.get('retry') else 1
            meta = {**request.meta, 'retry': retry}
            request =  Request(url=request.url, meta=meta, headers=request.headers, callback=request.callback,
                           dont_filter=True)
        else:
            d = self._print_data(request, title=f'retrying more tha {n} times')
            write_in_a_file('retry > n', d, 'z_retry_many_times.txt')
            raise IgnoreRequest(f'The request has been failed {n} times')
        return request

    def _check_proxy_and_ua(self, request, response=None):
        """
        If there is a response and its status is 200, the proxy and the ua from the request are taken to do all the requests
        with these values.
        Else, the proxy and ua 'valid' values are set to None, because something has failed in the request.
        :param request:
        :param response:
        """
        try:
            if response and (response.status == 200):
                PUADownloaderMiddleware.proxy = request.meta.get('proxy_source')
                PUADownloaderMiddleware.ua = request.headers.get(b'User-Agent')
            elif PUADownloaderMiddleware.proxy == request.meta.get('proxy_source'):
                d = self._print_data(request, title='VALID PROXY HAS FAILED', exception=exception)
                write_in_a_file('EXCEPTION', d, 'z_exception_with_a_valida_proxy.txt')
                print('** Valid proxy has failed')
                PUADownloaderMiddleware.proxy = None
                PUADownloaderMiddleware.ua = None
        except:
            pass

    def process_request(self, request, spider):
        if request.meta.get('ignore'):
            print(f'!!ERDownloaderMiddleware ignore {request.url}')
            raise IgnoreRequest(f'Ignore request: {request.url}')

    def process_exception(self, request, exception, spider):
        print(f'* ERDownloaderMiddleware exception: {exception} of type {type(exception)}')
        if type(exception) == IgnoreRequest or request.meta.get('ignore'):
            print(f'* IgnoreRequest: The request will be ignore: {request.url}')
            return None
        else:
            d = self._print_data(request, title='EXCEPTION WITH', exception=exception)
            write_in_a_file('EXCEPTION', d, 'z_exception.txt')
            self._check_proxy_and_ua(request)
            return self._make_the_request_again(request)

    def process_response(self, request, response, spider):
        self._check_proxy_and_ua(request, response)
        if response.status == 200:
            d = self._print_data(request, 'VALID RESPONSE')
            write_in_a_file('VAlID RESPONSE', d, 'z_valid_request.txt')
            return response
        else:
            print(f'!!!! response.status: {response.status}');
            print(f'response: {response}')
            print(f'response: {dir(response)}')
            print(f'request: {request}')
            print(f'request: {dir(request)}')
            # https://www.lightspeedsystems.com/
            d = self._print_data(request, f'NOT A VALID RESPONSE: {response.status}')
            write_in_a_file('NOT A VAlID RESPONSE', d, 'z_not_a_valid_request.txt')
            return self._make_the_request_again(request)


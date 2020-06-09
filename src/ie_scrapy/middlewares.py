# -*- coding: utf-8 -*-
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
from job.models import Job, Company
import logging
logging.getLogger().setLevel(logging.INFO)


class CheckDownloaderMiddleware(object):

   def process_request(self, request, spider):
        url = request.url
        if ('ofertasdetrabajo' in url) or ('ofertasempresa' in url) or ('colaboradoras' in url):
            model = Job if 'ofertasdetrabajo' in url else Company
            try:
                instance = model.objects.get(link=url)
            except:
                return None
            if (instance.checked_at.date() == timezone.localtime(timezone.now()).date() or
                instance.checked_at.date() == timezone.localtime(timezone.now()).date() - relativedelta(days=1)
            ):
                request.meta.update({'ignore': True})
                raise IgnoreRequest(f'Ignore request: {request.url}')
            else:
                return None
        elif not 'www.infoempleo.com' in url:
            request.meta.update({'ignore': True})
            raise IgnoreRequest(request.url)
        else:
            return None


class PUADownloaderMiddleware(object):

    max_retry = 80
    proxy = None
    ua = None

    def _make_the_request_again(self, request, response=None):
        n = PUADownloaderMiddleware.max_retry
        if ('robots' in request.url) and request.meta.get('retry', 0) > 5:
            raise IgnoreRequest(f'The request {request.url} has been failed {n} times')
        elif (response and response.status == 404) and (request.meta.get('retry', 0) > 5):
            raise IgnoreRequest(f'The request {request.url} has been failed {n} times with status {response.status}')
        elif request.meta.get('retry', 0) < n:
            logging.info(f'Retrying {request.url} request for {request.meta.get("retry", 0)} time')
            retry = request.meta['retry'] + 1 if request.meta.get('retry') else 1
            meta = {**request.meta, 'retry': retry}
            request =  Request(url=request.url, meta=meta, headers=request.headers, callback=request.callback,
                           dont_filter=True)
        else:
            raise IgnoreRequest(f'The request {request.url} has been failed {n} times')
        return request

    def _check_proxy_and_ua(self, request, spider, response=None):
        """
        If there is a response and its status is 200, the proxy and the ua from the request are taken to do all the requests
        with these values.
        Else, the proxy and ua 'valid' values are set to None, because something has failed in the request.
        :param request: request
        :param response: response
        """
        try:
            if response and (response.status == 200):
                PUADownloaderMiddleware.proxy = request.meta.get('proxy_source')
                PUADownloaderMiddleware.ua = request.headers.get(b'User-Agent')
            elif PUADownloaderMiddleware.proxy == request.meta.get('proxy_source'):
                PUADownloaderMiddleware.proxy = None
                PUADownloaderMiddleware.ua = None
        except Exception as e:
            spider.logger.warning(f'_check_proxy_and_ua exception: {e}')

    def process_request(self, request, spider):
        """
        Set the last valid proxy and user agent in the request
        """
        logging.info(f'Initial proxy {request.meta.get("proxy_source")}')
        if PUADownloaderMiddleware.proxy:
            request.meta.update({'proxy_source': PUADownloaderMiddleware.proxy})
            request.meta.update({'proxy':
                                     f'{PUADownloaderMiddleware.proxy.type}://{PUADownloaderMiddleware.proxy.host}:{PUADownloaderMiddleware.proxy.port}'})
            request.headers.update({b'User-Agent': [PUADownloaderMiddleware.ua]})
        logging.info(f'Final proxy {request.meta.get("proxy_source")}')

    def process_exception(self, request, exception, spider):
        if type(exception) == IgnoreRequest or request.meta.get('ignore'):
            logging.info(f'Ignoring {request.url} request with proxy {request.meta.get("proxy_source")}')
            request.meta.get('retry', 0)
            return None
        else:
            logging.info(f'Exception in {request.url} request')
            logging.info(f'Exception {exception}')
            self._check_proxy_and_ua(request, spider)
            result = self._make_the_request_again(request)
            return result

    def process_response(self, request, response, spider):
        self._check_proxy_and_ua(request, spider, response)
        if response.status == 200:
            logging.info(f'Request {request.url} processed with proxy {request.meta.get("proxy_source")}')
            return response
        else:
            result = self._make_the_request_again(request, response)
            return result
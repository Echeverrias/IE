from collections import namedtuple
from scrapy.http import Request, Response
from scrapy.exceptions import IgnoreRequest
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from ie_scrapy.middlewares import CheckDownloaderMiddleware, PUADownloaderMiddleware, ERDownloaderMiddleware
from job.models import Job, Company
from django.test import TestCase
from scrapy.spiders import Spider

Proxy = namedtuple('Proxy', 'host port code country anonymous type source')

class FakeRequest():
    valid_proxy = Proxy(host='192.200.200.86', port='3128', code='us', country='united states', anonymous=False,
                        type='http',
                        source='us-proxy')
    invalid_proxy = Proxy(host='000.000.000.00', port='00000', code='us', country='united states', anonymous=False,
                          type='http', source='us-proxy')
    invalid_ua = b'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    valid_ua = b'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'

    @staticmethod
    def get_request(url='http://test', proxy=valid_proxy, ua=valid_ua, meta={}, headers={}):
        meta.update({'proxy_source': proxy})
        meta.update({'proxy':
                         f'{proxy.type}://{proxy.host}:{proxy.port}'})
        headers.update({b'User-Agent': [ua]})
        return Request(url=url, meta=meta, headers=headers)

    @staticmethod
    def get_valid_request(url='http://test', meta={}, headers={}):
        meta.update({'proxy_source': FakeRequest.valid_proxy})
        meta.update({'proxy':
                         f'{FakeRequest.valid_proxy.type}://{FakeRequest.valid_proxy.host}:{FakeRequest.valid_proxy.port}'})
        headers.update({b'User-Agent': [FakeRequest.valid_ua]})
        return Request(url=url, meta=meta, headers=headers)

    @staticmethod
    def get_invalid_request(url='http://test', meta={}, headers={}):
        meta.update({'proxy_source': FakeRequest.invalid_proxy})
        meta.update({'proxy':
                         f'{FakeRequest.invalid_proxy.type}://{FakeRequest.invalid_proxy.host}:{FakeRequest.invalid_proxy.port}'})
        headers.update({b'User-Agent': [FakeRequest.invalid_ua]})
        return Request(url=url, meta=meta, headers=headers)


class FakeResponse():

    @staticmethod
    def get_valid_response(url='http://test'):
        return Response(url, status=200)

    @staticmethod
    def get_invalid_response(url='http://test'):
        invalid_status = [404]
        return Response(url, status=invalid_status[0])

class TestERDownloaderMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.erdm = ERDownloaderMiddleware()
        cls.fake_spider = Spider(name="fake")

    def test_process_request(self):
        request = FakeRequest.get_valid_request('http://test', meta={'ignore': True})
        try:
            exception = None
            self.erdm.process_request(request, None)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)
        request = FakeRequest.get_valid_request('http://test')
        self.assertIsNone(self.erdm.process_request(request, None))

    def test_make_the_request_again(self):
        request = FakeRequest.get_valid_request('http://test')
        request_ = self.erdm._make_the_request_again(request)
        self.assertIsInstance(request_, Request)
        self.assertEqual(request_.meta.get('retry'), 1)
        request = FakeRequest.get_valid_request('http://test', meta={'retry': 3})
        request_ = self.erdm._make_the_request_again(request)
        self.assertIsInstance(request_, Request)
        self.assertEqual(request_.meta.get('retry'), 4)
        request = FakeRequest.get_valid_request('http://test', meta={'retry': ERDownloaderMiddleware.max_retry + 1})
        try:
            exception = None
            self.erdm._make_the_request_again(request)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)

    def test_check_proxy_and_ua(self):
        # 1. Valid response (gets the valid proxy, ua pair)
        request = FakeRequest.get_valid_request('http://test')
        response = FakeResponse.get_valid_response('http://test')
        self.erdm._check_proxy_and_ua(request, self.fake_spider, response)
        self.assertEqual(PUADownloaderMiddleware.proxy, request.meta.get('proxy_source'))
        self.assertEqual(PUADownloaderMiddleware.ua, request.headers.get(b'User-Agent'))
        # 2. Not a valid response from an invalid request (invalid proxy)
        request = FakeRequest.get_invalid_request('http://test')
        response = FakeResponse.get_invalid_response('http://test')
        self.erdm._check_proxy_and_ua(request, self.fake_spider, response)
        self.assertEqual(PUADownloaderMiddleware.proxy, FakeRequest.valid_proxy)
        self.assertEqual(PUADownloaderMiddleware.ua, FakeRequest.valid_ua)
        # 3. Not a valid response from a valid request (sets the valid proxy, ua pair) to None)
        request = FakeRequest.get_valid_request('http://test')
        response = FakeResponse.get_invalid_response('http://test')
        self.erdm._check_proxy_and_ua(request, self.fake_spider, response)
        self.assertIsNone(PUADownloaderMiddleware.proxy)
        self.assertIsNone(PUADownloaderMiddleware.ua,)

    def test_process_exception(self):
        PUADownloaderMiddleware.proxy = FakeRequest.valid_proxy
        PUADownloaderMiddleware.ua =FakeRequest.valid_ua
        # IgnoreRequest Exception
        request = FakeRequest.get_valid_request(meta={'ignore':True})
        self.assertIsNone(self.erdm.process_exception(request, Exception('fake'), self.fake_spider))
        self.assertEqual(PUADownloaderMiddleware.proxy, request.meta.get('proxy_source'))
        self.assertEqual(PUADownloaderMiddleware.ua, request.headers.get(b'User-Agent'))
        request = FakeRequest.get_valid_request('http://test')
        self.assertIsNone(self.erdm.process_exception(request, IgnoreRequest(), self.fake_spider))
        self.assertEqual(PUADownloaderMiddleware.proxy, request.meta.get('proxy_source'))
        self.assertEqual(PUADownloaderMiddleware.ua, request.headers.get(b'User-Agent'))
        # Other Exception
        request = FakeRequest.get_valid_request('http://test')
        request_ = self.erdm.process_exception(request, Exception('fake'), self.fake_spider)
        self.assertIsInstance(request_, Request)
        self.assertEqual(request_.meta.get('retry'), 1)
        self.assertIsNone(PUADownloaderMiddleware.proxy)
        self.assertIsNone(PUADownloaderMiddleware.ua)
        request = FakeRequest.get_valid_request('http://test', meta={'retry': ERDownloaderMiddleware.max_retry + 1})
        try:
            exception = None
            self.erdm.process_exception(request, Exception('fake'), self.fake_spider)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)
        self.assertIsNone(PUADownloaderMiddleware.proxy)
        self.assertIsNone(PUADownloaderMiddleware.ua)

    def test_process_response(self):
        PUADownloaderMiddleware.proxy = None
        PUADownloaderMiddleware.ua = None
        # Valid response
        request = FakeRequest.get_valid_request()
        response = FakeResponse.get_valid_response()
        self.assertIsInstance(self.erdm.process_response(request, response, self.fake_spider), Response)
        self.assertEqual(PUADownloaderMiddleware.proxy, request.meta.get('proxy_source'))
        self.assertEqual(PUADownloaderMiddleware.ua, request.headers.get(b'User-Agent'))
        # Invalid response
        response = FakeResponse.get_invalid_response()
        self.assertIsInstance(self.erdm.process_response(request, response, self.fake_spider), Request)
        self.assertIsNone(PUADownloaderMiddleware.proxy)
        self.assertIsNone(PUADownloaderMiddleware.ua)
        request = FakeRequest.get_valid_request(meta={'retry':  ERDownloaderMiddleware.max_retry + 1})
        try:
            exception = None
            self.erdm.process_response(request, response, self.fake_spider)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)
        self.assertIsNone(PUADownloaderMiddleware.proxy)
        self.assertIsNone(PUADownloaderMiddleware.ua)


class TestPUADownloaderMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.puadm = PUADownloaderMiddleware()

    def test_process_request(self):
        PUADownloaderMiddleware.proxy = FakeRequest.valid_proxy
        PUADownloaderMiddleware.ua = FakeRequest.valid_ua
        request = FakeRequest.get_request("https://Test", FakeRequest.invalid_proxy, FakeRequest.invalid_ua)
        self.assertIsNone(self.puadm.process_request(request, None))
        self.assertEqual(request.meta.get('proxy_source'), PUADownloaderMiddleware.proxy)
        self.assertEqual(request.headers.get(b'User-Agent'), PUADownloaderMiddleware.ua)
        request = FakeRequest.get_request("https://Test", FakeRequest.valid_proxy, FakeRequest.valid_ua)
        self.assertIsNone(TestPUADownloaderMiddleware.puadm.process_request(request, None))
        self.assertEqual(request.meta.get('proxy_source'), PUADownloaderMiddleware.proxy)
        self.assertEqual(request.headers.get(b'User-Agent'), PUADownloaderMiddleware.ua)
        PUADownloaderMiddleware.proxy = None
        PUADownloaderMiddleware.ua = None
        request = FakeRequest.get_request("https://Test", FakeRequest.invalid_proxy, FakeRequest.invalid_ua)
        self.assertIsNone(TestPUADownloaderMiddleware.puadm.process_request(request, None))
        self.assertEqual(request.meta.get('proxy_source'), FakeRequest.invalid_proxy)
        self.assertEqual(request.headers.get(b'User-Agent'), FakeRequest.invalid_ua)


class TestCheckDownloaderMiddleware(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.checkdm = CheckDownloaderMiddleware()
        today = timezone.localtime(timezone.now())
        yesterday = today - relativedelta(days=1)
        before_yesterday = today - relativedelta(days=2)
        old_date = before_yesterday
        # Recent scrapped offer
        cls.recent_scrapped_offer_id = 555
        cls.recent_scrapped_offer_url = f"https://www.infoempleo.com/ofertasdetrabajo/auxiliar/alredores-de-londres/{cls.recent_scrapped_offer_id}/"
        Job.objects.create(id=cls.recent_scrapped_offer_id, link=cls.recent_scrapped_offer_url, name="auxiliar")
        # Not recent scrapped offer
        cls.not_recent_scrapped_offer_id = 777
        cls.not_recent_scrapped_offer_url = f"https://www.infoempleo.com/ofertasdetrabajo/auxiliar/estocolmo/{cls.not_recent_scrapped_offer_id}/"
        Job.objects.create(id=cls.not_recent_scrapped_offer_id, link=cls.not_recent_scrapped_offer_url, name="auxiliar")
        Job.objects.filter(id=cls.not_recent_scrapped_offer_id).update(checked_at=old_date)
        # New offer
        cls.new_offer_url = f"https://www.infoempleo.com/ofertasdetrabajo/auxiliar/estocolmo/888/"
        # Recent scrapped company
        cls.recent_scrapped_company_url = f"https://www.infoempleo.com/ofertasempresa/reach-health-recruitment/555/"
        Company.objects.create(link=cls.recent_scrapped_company_url, reference=555, name="reach-health-recruitment" )
        # Not recent scrapped company
        cls.not_recent_scrapped_company_url = f"https://www.infoempleo.com/ofertasempresa/adecco/777/"
        Company.objects.create(link=cls.not_recent_scrapped_company_url, reference=777, name="adecco")
        Company.objects.filter(link=cls.not_recent_scrapped_company_url).update(checked_at=old_date)
        # New company
        cls.new_company_url = f"https://www.infoempleo.com/ofertasempresa/vodafone/888/"
        # Not domain url
        cls.not_domain_url = "https://docs.python.org/3/library/unittest.html"
        # Some domain url
        cls.some_domain_url = "https://www.infoempleo.com/xxx/xxx.html"

    def test_process_request(self):
        # Requests processed today
        request = FakeRequest.get_request(self.recent_scrapped_offer_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        try:
            exception = None
            self.checkdm.process_request(request, None)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)
        request = FakeRequest.get_request(self.recent_scrapped_company_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        try:
            exception = None
            self.checkdm.process_request(request, None)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)
        # New requests
        request = FakeRequest.get_request(self.new_offer_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        self.assertIsNone(self.checkdm.process_request(request, None))
        request = FakeRequest.get_request(self.new_company_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        self.assertIsNone(self.checkdm.process_request(request, None))
        # Not recent requests
        request = FakeRequest.get_request(self.not_recent_scrapped_offer_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        self.assertIsNone(self.checkdm.process_request(request, None))
        request = FakeRequest.get_request(self.not_recent_scrapped_company_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        self.assertIsNone(self.checkdm.process_request(request, None))
        # Not domain url
        request = FakeRequest.get_request(self.not_domain_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        try:
            exception = None
            self.checkdm.process_request(request, None)
        except IgnoreRequest as e:
            exception = e
        finally:
            self.assertIsInstance(exception, IgnoreRequest)
        # Some domain url
        request = FakeRequest.get_request(self.some_domain_url, FakeRequest.valid_proxy, FakeRequest.valid_ua)
        self.assertIsNone(self.checkdm.process_request(request, None))









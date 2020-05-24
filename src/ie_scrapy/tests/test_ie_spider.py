import os
from scrapy.http import HtmlResponse, Request
from django.test import TestCase
from collections import namedtuple
from job.models import Job, Company
from ie_scrapy.items import JobItem, CompanyItem
from ie_scrapy.spiders.ie import InfoempleoSpider, PageNotFoundError, NoExistentPageError, NoElementFoundError

BASE_DIR = os.path.dirname(__file__)
InfoResults = namedtuple('ResultsNumberInfo',['first_result_showed', 'last_result_showed', 'total_results'])

class FakeResponse():

    @staticmethod
    def _fake_response_from_file(file_name, url=None, meta={}):
        """
        Create a Scrapy fake HTTP response from a HTML file
        @param file_name: a string with the path to the file.
        @param url: a string with the URL of the response.
        returns: A Scrapy HTTP response.
        """
        if not url:
            url = 'http://www.infoempleo.com'
        file_path = os.path.join(BASE_DIR, 'data', file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=file_content, encoding='utf-8')
        return response, meta

    @staticmethod
    def get_offers_results_first_page_response():
        url = 'https://www.infoempleo.com/ofertas-internacionales/'
        filename= "offers_results_first_page_1_20_1492.html"
        meta = {'_info_results': InfoResults(1,20, 1492), '_page': 1}
        return FakeResponse._fake_response_from_file(filename, url, meta)

    @staticmethod
    def get_offers_results_last_page_response():
        url = 'https://www.infoempleo.com/trabajo/'
        filename= "offers_results_last_page_1_18_18.html"
        meta = {'_info_results': InfoResults(1, 18, 18), '_page': 1}
        return FakeResponse._fake_response_from_file(filename, url, meta)

    @staticmethod
    def get_offers_results_response():
        url = 'https://www.infoempleo.com/ofertas-internacionales/?pagina=5'
        filename = "offers_results_81_100_1492.html"
        meta = {'_info_results': InfoResults(81, 100, 1492), '_page': 5}
        return FakeResponse._fake_response_from_file(filename, url, meta)

    @staticmethod
    def get_offer_response():
        url = 'https://www.infoempleo.com/ofertasdetrabajo/operarioa-metal/mostoles/2459763/'
        filename = "offer.html"
        return FakeResponse._fake_response_from_file(filename, url)

    @staticmethod
    def get_company_response():
        url = 'https://www.infoempleo.com/ofertasempresa/iman-temporing-ett-s-l/7347/'
        filename = "company.html"
        return FakeResponse._fake_response_from_file(filename, url)

    @staticmethod
    def get_404_response():
        url = 'https://www.infoempleo.com/ofertas-internacionales/?pagina=500'
        filename = "error_404.html"
        return FakeResponse._fake_response_from_file(filename, url)

class TestInfoempleoSpider(TestCase):

    ie = InfoempleoSpider()
    @classmethod
    def setUpTestData(cls):
        cls.ie = InfoempleoSpider()

    def test_parse(self):
        # Getting the last page
        response, meta = FakeResponse.get_offers_results_last_page_response()
        for offer_req in TestInfoempleoSpider.ie.parse(response):
           self.assertIn('https://www.infoempleo.com/ofertasdetrabajo/', offer_req.url)
           self.assertEqual(offer_req.callback, TestInfoempleoSpider.ie.parse_item)
        # Getting the first page
        response, meta = FakeResponse.get_offers_results_first_page_response()
        for i, offer_req in enumerate(TestInfoempleoSpider.ie.parse(response)):
            if i < 20:
                self.assertIn('https://www.infoempleo.com/ofertasdetrabajo/', offer_req.url)
                self.assertEqual(offer_req.callback, TestInfoempleoSpider.ie.parse_item)
            else:
                isep = offer_req.url.rfind('/')
                url = offer_req.url[0:isep]
                self.assertIn(url, offer_req.url)
                self.assertEqual(offer_req.callback, TestInfoempleoSpider.ie.parse)

    def test_get_info_of_number_of_results(self):
        response, meta = FakeResponse.get_offers_results_last_page_response()
        self.assertEqual(TestInfoempleoSpider.ie._get_info_of_number_of_results(response),
                         meta.get('_info_results'))
        response = FakeResponse.get_404_response()
        try:
            exception=None
            TestInfoempleoSpider.ie._get_info_of_number_of_results(response)
        except Exception as e:
            exception = e
        finally:
            self.assertIsInstance(exception, NoElementFoundError)

    def test_get_the_total_number_of_results(self):
        response, meta = FakeResponse.get_offers_results_last_page_response()
        self.assertEqual(TestInfoempleoSpider.ie._get_the_total_number_of_results(response),
                         meta.get('_info_results').total_results)
        response = FakeResponse.get_404_response()
        try:
            exception = None
            TestInfoempleoSpider.ie._get_the_total_number_of_results(response)
        except Exception as e:
            exception = e
        finally:
            self.assertIsInstance(exception, NoElementFoundError)

    def _is_there_next_page(self):
        response, meta = FakeResponse.get_offers_results_response()
        self.assertTrue(TestInfoempleoSpider.ie._is_there_next_page(response))
        response, meta = FakeResponse.get_offers_results_last_page_response()
        self.assertFalse(TestInfoempleoSpider.ie._is_there_next_page(response))
        response = FakeResponse.get_404_response()
        try:
            exception = None
            TestInfoempleoSpider.ie._is_there_next_page(response)
        except Exception as e:
            exception = e
        finally:
            self.assertIsInstance(exception, NoExistentPageError)

    def test_clean_url(self):
        response, meta = FakeResponse.get_offers_results_response()
        isep = response.url.rfind('/')
        self.assertEqual(TestInfoempleoSpider.ie._clean_url(response.url), response.url[0:isep+1])

    def test_get_next_page_url(self):
        response, meta = FakeResponse.get_offers_results_response()
        response_page = meta.get('_page')
        next_page = response.url.replace(str(response_page), str(response_page + 1))
        self.assertEqual(TestInfoempleoSpider.ie._get_next_page_url(response.url), next_page)
        response, meta = FakeResponse.get_offers_results_first_page_response()
        next_page = response.url + "?pagina=2"
        self.assertEqual(TestInfoempleoSpider.ie._get_next_page_url(response.url), next_page)
        page = 4
        next_page = f'{response.url}?pagina={page}'
        self.assertEqual(TestInfoempleoSpider.ie._get_next_page_url(response.url, next_page=page), next_page)







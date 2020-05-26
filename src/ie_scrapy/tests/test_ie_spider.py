import os
from scrapy.http.request import Request
from scrapy.http.response.html import HtmlResponse
from django.test import TestCase
from collections import namedtuple
from job.models import Job, Company
from ie_scrapy.items import JobItem, CompanyItem
from ie_scrapy.spiders.ie import InfoempleoSpider, PageNotFoundError, NoExistentPageError, NoElementFoundError
import pickle

BASE_DIR = os.path.dirname(__file__)
InfoResults = namedtuple('ResultsNumberInfo',['first_result_showed', 'last_result_showed', 'total_results'])

class FakeResponse():

    @staticmethod
    def _get_object_from_a_file(file_name):
        file_path = os.path.join(BASE_DIR, 'data', file_name)
        if file_name.endswith('.html'):
            with open(file_path, 'r', encoding='utf-8') as f:
                object = f.read().replace('\n', '\r\n')
        else:
            with open(file_path, 'rb') as f:
                object = pickle.load(f)
        return object

    @staticmethod
    def _fake_response_from_file(file_name, url=None, meta= {}, data={}):
        """
        Create a Scrapy fake HTTP response from a HTML file
        @param file_name: a string with the path to the file.
        @param url: a string with the URL of the response.
        returns: A Scrapy HTTP response.
        """
        if not url:
            url = 'http://www.infoempleo.com'
        object = FakeResponse._get_object_from_a_file(file_name)
        if file_name.endswith('.html'):
            request = Request(url=url)
            response = HtmlResponse(url=url, request=request, body=object, encoding='utf-8')
            response.meta.update(meta)
        else:
            response = object
        return response, data


    @staticmethod
    def get_offers_results_first_page_response():
        url = 'https://www.infoempleo.com/ofertas-internacionales/'
        filename= "offers_results_first_page_1_20_1492.html"
        data = {'_info_results': InfoResults(1,20, 1492), '_page': 1}
        return FakeResponse._fake_response_from_file(filename, url, data=data)

    @staticmethod
    def get_offers_results_last_page_response():
        url = 'https://www.infoempleo.com/trabajo/'
        filename= "offers_results_last_page_1_18_18.html"
        data = {'_info_results': InfoResults(1, 18, 18), '_page': 1}
        return FakeResponse._fake_response_from_file(filename, url, data=data)

    @staticmethod
    def get_offers_results_response():
        url = 'https://www.infoempleo.com/ofertas-internacionales/?pagina=5'
        filename = "offers_results_81_100_1492.html"
        data = {'_info_results': InfoResults(81, 100, 1492), '_page': 5}
        return FakeResponse._fake_response_from_file(filename, url, data=data)

    @staticmethod
    def get_offer_response():
        url = 'https://www.infoempleo.com/ofertasdetrabajo/operarioa-metal/mostoles/2459763/'
        filename = "offer.html"
        meta = {"start_url":  'https://www.infoempleo.com/trabajo/area-de-empresa_legal/'}
        company_dict = FakeResponse._get_object_from_a_file('company_info.dict')
        job_dict = FakeResponse._get_object_from_a_file('job_info.dict')
        job_item = FakeResponse._get_object_from_a_file('job_item.item')
        # In a real response the domain is not included in the links so it is added
        domain = 'https://www.infoempleo.com'
        link = company_dict['link']
        company_dict['link'] = domain + link if domain not in link else link
        link = job_dict['link']
        job_dict['link'] = domain + link if domain not in link else link
        job_item['link'] = job_dict['link']
        job_item['company']['link'] = company_dict['link']
        data = {
            'company_dict': company_dict,
            'job_dict': job_dict,
            'job_item': job_item,
        }
        return FakeResponse._fake_response_from_file(filename, url, meta=meta, data=data)

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
        response, data = FakeResponse.get_offers_results_last_page_response()
        for offer_req in self.ie.parse(response):
           self.assertIn('https://www.infoempleo.com/ofertasdetrabajo/', offer_req.url)
           self.assertEqual(offer_req.callback, self.ie.parse_item)
        # Getting the first page
        response, data = FakeResponse.get_offers_results_first_page_response()
        for i, offer_req in enumerate(self.ie.parse(response)):
            if i < 20:
                self.assertIn('https://www.infoempleo.com/ofertasdetrabajo/', offer_req.url)
                self.assertEqual(offer_req.callback, self.ie.parse_item)
            else:
                isep = offer_req.url.rfind('/')
                url = offer_req.url[0:isep]
                self.assertIn(url, offer_req.url)
                self.assertEqual(offer_req.callback, self.ie.parse)

    def test_get_info_of_number_of_results(self):
        response, data = FakeResponse.get_offers_results_last_page_response()
        self.assertEqual(self.ie._get_info_of_number_of_results(response),
                         data.get('_info_results'))
        response = FakeResponse.get_404_response()
        try:
            exception=None
            self.ie._get_info_of_number_of_results(response)
        except Exception as e:
            exception = e
        finally:
            self.assertIsInstance(exception, NoElementFoundError)

    def test_get_the_total_number_of_results(self):
        response, data = FakeResponse.get_offers_results_last_page_response()
        self.assertEqual(self.ie._get_the_total_number_of_results(response),
                         data.get('_info_results').total_results)
        response = FakeResponse.get_404_response()
        try:
            exception = None
            self.ie._get_the_total_number_of_results(response)
        except Exception as e:
            exception = e
        finally:
            self.assertIsInstance(exception, NoElementFoundError)

    def test_is_there_next_page(self):
        response, data = FakeResponse.get_offers_results_response()
        self.assertTrue(self.ie._is_there_next_page(response))
        response, data = FakeResponse.get_offers_results_last_page_response()
        self.assertFalse(self.ie._is_there_next_page(response))
        response = FakeResponse.get_404_response()
        try:
            exception = None
            self.ie._is_there_next_page(response)
        except Exception as e:
            exception = e
        finally:
            self.assertIsInstance(exception, NoExistentPageError)

    def test_clean_url(self):
        response, data = FakeResponse.get_offers_results_response()
        isep = response.url.rfind('/')
        self.assertEqual(self.ie._clean_url(response.url), response.url[0:isep+1])

    def test_get_next_page_url(self):
        response, data = FakeResponse.get_offers_results_response()
        response_page = data.get('_page')
        next_page = response.url.replace(str(response_page), str(response_page + 1))
        self.assertEqual(self.ie._get_next_page_url(response.url), next_page)
        response, data = FakeResponse.get_offers_results_first_page_response()
        next_page = response.url + "?pagina=2"
        self.assertEqual(self.ie._get_next_page_url(response.url), next_page)
        page = 4
        next_page = f'{response.url}?pagina={page}'
        self.assertEqual(self.ie._get_next_page_url(response.url, next_page=page), next_page)
        
    def test_extract_company_info(self):
        response, data = FakeResponse.get_offer_response()
        company_dict = self.ie._get_company_info(response)
        self.assertEqual(company_dict, data.get('company_dict'))

    def test_extract_job_info(self):
        response, data = FakeResponse.get_offer_response()
        job_info = self.ie._get_job_info(response)
        self.assertEqual(job_info, data.get('job_dict'))

    def test_parse_item(self):
        response, data = FakeResponse.get_offer_response()
        gen = self.ie.parse_item(response)
        for ji in gen:
            self.assertEqual(ji, data.get('job_item'))

# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import JobItem
import re
import time


class Infoempleo2Spider(CrawlSpider):
    name = 'ie2'
    allowed_domains = ['infoempleo.com']

    start_urls = ["https://www.infoempleo.com/trabajo/",
                  "https://www.infoempleo.com/ofertas-internacionales/"]



    """
    rules = (
        Rule(
            LinkExtractor(allow=(r'https://www.infoempleo.com/ofertasdetrabajo/.'), restrict_xpaths=("//*[@id='main-content']/div[2]/ul/li/h2/a")),
            callback="parse_item"),
    )
    """
    rules = (
        Rule(
            LinkExtractor(restrict_xpaths=("//*[@id='main-content']/div[2]/ul/li/h2/a")),
            callback="parse_item"),
    )


    def parse_start_url(self, response):
        print("*****************************************************")
        print("do something with the start url")
        return self.parse_page(response)
    

    def parse_page(self, response):
        print('PARSE')
        print(response.url)

        if self.__is_there_next_page(response):
            next_url = self.__get_next_page_url(response)
            print('go to next url %s' % next_url) ##
            yield response.follow(next_url, self.parse_page)


    def __is_there_next_page(self, response):
        print('__is_there_next_page')
        results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
        print(results_showed)
        text = results_showed.replace('-', ' ')  # Mostrando 1-20 de 1028 ofertas
        print  ##
        print(text)
        print  ##
        numbers = [int(s) for s in text.split() if s.isdigit()]
        print(numbers)
        return numbers[1] < numbers[2]
        #return numbers[1] > 40 #%


    def __get_next_page_url(self, response):
        print('* get_next_page_url')
        actual_url = response.url
        print(actual_url)
        try:
            init_url = re.findall(self.start_urls[0] + '|' + self.start_urls[1], actual_url)[0]
            #init_url = re.findall(self.start_urls[0], actual_url)[0] #%
            print('init_url: %s'%init_url)
            try:
                next_page = int(re.findall(r'\d+', actual_url)[0]) + 1
                print(next_page)
            except:
                next_page = 2
            return init_url + str(next_page) + '/'
        except Exception as e:
            print('Error getting next page url: %s' % e)
            return actual_url

        
    def parse_item(self, response):
        print('PARSE_ITEM')
        print (response.url)



        ie_dict = {
            'link': response.url,
            'registered_people': response.xpath("//div[@class='main-title']//ul[@class='meta']/li/span/text()").extract_first(),
            'id': response.xpath("(//div[@class='main-title']//ul[@class='details inline']/li/text())[1]").extract_first(),
            'company_link': response.xpath("//div[@class='main-title']//ul[@class='details inline'][1]//li/a/@href").extract_first(),
            'job_date': response.xpath("//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/text()").extract_first(),
            'summary': response.xpath("//div[@class='main-title']//p/text()").extract_first(),
            'nationality': response.xpath("//nav[@class='breadcrumbs']//li[2]/a/text()").extract_first(),
            'city': response.xpath("//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()").extract_first(),
            'country': response.xpath("//nav[@class='breadcrumbs']//li[3]/a/text()").extract_first(),
            'name': response.xpath("//nav[@class='breadcrumbs']//li[5]/text()").extract_first(),
            'description': response.xpath("//div[@class='offer']//div[@class='dtable']//p/text()").extract_first(),
            'functions':response.xpath("//div[@class='offer']//h3[contains(text(), 'Funciones')]//following-sibling::pre[1]/text()").extract_first(),
            'requirements': response.xpath("//div[@class='offer']//h3[contains(text(), 'Requisitos')]//following-sibling::pre[1]/text()").extract_first(),
            'it_is_offered': response.xpath("//div[@class='offer']//h3[contains(text(), 'Se ofrece')]//following-sibling::pre[1]/text()").extract_first(),
            'tags': response.xpath("//div[@class='offer']//h3[contains(text(), 'Etiquetas')]//following-sibling::ul[@class='tags']/li/text()").extract_first(),
            'area': response.xpath("//div[@class='offer']//h3[contains(text(), 'Área')]//following-sibling::p[1]/text()").extract_first(),
            'category_level': response.xpath("//div[@class='offer']//h3[contains(text(), 'ategoría')or contains(text(), 'ivel')]//following-sibling::p[1]/text()").extract_first(),
            'vacancies': response.xpath("//div[@class='offer']//h3[contains(text(), 'Vacantes')]//following-sibling::p[1]/text()").extract_first(),
            'company_name': self.__get_company_name(response),
            'company_description': response.xpath("//div[@class='company']//pre/text()").extract_first(),
            'company_city': response.xpath("//div[@class='company']//*[contains(@class,'details')]/li[1]/text()").extract_first(),
            'company_category': response.xpath("//div[@class='company']//*[contains(@class,'details')]/li[2]/text()").extract_first(),
        }
        #
        #'company': response.xpath("//div[@class='main-title']//ul[@class='details inline'][1]//li/a/text()").extract_first(),
        # El orden en el que se asignan los valores será su  orden
        #ie = JobItem(ie_dict)
        yield ie_dict


    def __get_company_name(self, response):
        company_name = response.xpath("//div[@class='company']//*[@class='title']/text()").extract_first()
        if not company_name:
            company_name = response.xpath("//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()").extract_first()
            if not company_name:
                company_name = '?'
        return company_name


    def parse_fake(self, response):
        print('PARSE')
        print(response.url)
        i = self.get_fake_job_item()
        yield i



    def get_fake_job_item(self):
        print('yield_job_item')
        ie_dict = {
            'link': "https://medium.com/dreamcatcher-its-blog/making-an-stand-alone-executable-from-a-python-script-using-pyinstaller-d1df9170e263",
            'registered_people': 0,
            'id': 324 ,
            'company': 323,
            'job_date': None,
            'requisites': 'leer',
            'nationality': 'nacional',
            'area': 'rrhh',
            'city': 'Móstoles',
            'country': 'España',
            'name': 'trabajo prueba'
        }
        #
        # 'company': response.xpath("//div[@class='main-title']//ul[@class='details inline'][1]//li/a/text()").extract_first(),
        # El orden en el que se asignan los valores será su  orden
        ie = JobItem(ie_dict)
        return ie

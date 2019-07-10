# -*- coding: utf-8 -*-
from scrapy.spiders import Spider,CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from ..items import JobItem, StateItems
import math
import re
import random
import time



class InfoempleoSpider(Spider):
    name = 'ie'
    allowed_domains = ['infoempleo.com']

    start_urls = ["https://www.infoempleo.com/primer-empleo/",
                  "https://www.infoempleo.com/ofertas-internacionales/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_comercial-ventas/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_ingenieria-y-produccion/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_profesionales-artes-y-oficios/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_compras-logistica-y-transporte/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_sanidad-salud-y-servicios-sociales/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_hosteleria-turismo/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_administracion-de-empresas/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_administrativos-y-secretariado/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_atencion-al-cliente/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_banca-y-seguros/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_calidad-id-prl-y-medio-ambiente/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_construccion-e-inmobiliaria/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_educacion-formacion/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_internet/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_legal/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_marketing-y-comunicacion/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_medios-editorial-y-artes-graficas/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_recursos-humanos/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_tecnologia-e-informatica/",
                  "https://www.infoempleo.com/trabajo/area-de-empresa_telecomunicaciones/"
                  ]


    start_urls2 = ["https://www.infoempleo.com/trabajo/499/",
                  "https://www.infoempleo.com/ofertas-internacionales/45/"]

    start_urls3 = ["https://www.infoempleo.com/ofertas-internacionales/",
                   "https://www.infoempleo.com/trabajo/",
                   "https://www.infoempleo.com/primer-empleo/"]

    # start_urls = random.shuffle(urls, random.random) #No funciona


    allowed_hrefs = ["https://www.infoempleo.com/ofertas-internacionales/",
                  "https://www.infoempleo.com/trabajo/",
                  "https://www.infoempleo.com/primer-empleo/"]

    #start_urls = ["https://www.infoempleo.com/trabajo/353/"]



    def parse(self, response):
        print('PARSE')
        print(response.url)
        print('***************')
        print('***************')
        job_urls = response.xpath("//*[@id='main-content']/div[2]/ul/li/h2/a/@href").extract()
        print('%i jobs in this page' % len(job_urls))
        print('%i jobs in this page'%len(job_urls))

        for job_url in job_urls:
            print('# Go to job_url: %s', job_url)
            yield response.follow(job_url, self.parse_item, meta={"results_url": response.url})

            #yield Request(url=job_url, callback=self.parse_item, meta={"results_url": response.url})

        try:
            if self.__is_there_next_page(response):
                next_url = self.__get_next_page_url(response.url)
                print('#go to next url %s' % next_url) ##
                yield response.follow(next_url, self.parse)
            else:
                print('# All the pages have been parsed')
                #end_url = self.__clean_url(response.url)
                #yield response.follow(end_url, self.parse)
                print('# All the pages have been parsed')
        except:
            print('Selenium has told me that all the pages have been parsed')
        print ('after yield')


    def __is_there_next_page(self, response):
        print('__is_there_next_page')
        try:
            results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
            print(results_showed)
            text = results_showed.replace('-', ' ')  # Mostrando 1-20 de 1028 ofertas
            print  ##
            print(text)
            print  ##
            numbers = [int(s) for s in text.split() if s.isdigit()]
            print(numbers)
            return numbers[1] < numbers[2]

        except:
            try:
                page_not_found = response.xpath("//*[@class='error404']//div[3]/div/text()").extract_first().strip()
                print(page_not_found)
            except Exception as e:
                print('Error trying to find error 404: %s'%e)
            raise Exception('Not page found')
            return False

    """
    def __get_href(self, url):
        return re.findall(self.allowed_hrefs[0] + '|' + self.allowed_hrefs[1] + '|' + self.allowed_hrefs[2], url)[0]
    """

    def __clean_url2(self, url):
        page_path = re.findall('\d+/*', url)
        if page_path:
            url = url.replace(page_path[0], '')
        return url

    def __clean_url(self, url):

        try:
            url = re.findall('(.*/)\?pagina=\d+', url)[0]
        except:
            pass
        return url

    def __get_next_page_url(self, url):
        print('* get_next_page_url: %s'%url)
        try:
            #init_url = re.findall(self.start_urls[0] + '|' + self.start_urls[1], actual_url)[0]
            href = self.__clean_url(url)
            print('href: %s'%href)
            try:
                next_page = int(re.findall(r'\d+', url)[0]) + 1
                print(next_page)
            except:
                next_page = 2
            #return href + str(next_page) + '/' # ! important
            return href + '?pagina=' + str(next_page)

        except Exception as e:
            print('Error getting next page url: %s' % e)
            return url

        
    def parse_item(self, response):
        print('PARSE_ITEM')
        print (response.url)



        ie_dict = {
            'link': response.url,
            'registered_people': self.__extract_info(response, "//div[@class='main-title']//ul[@class='meta']/li/span/text()"),
            'id': self.__extract_info(response, "(//div[@class='main-title']//ul[@class='details inline']/li/text())[1]"),
            'company_link': self.__extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li/a/@href"),
            'job_date': self.__extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/text()"),
            'summary': self.__extract_info(response, "//div[@class='main-title']//p/text()"),
            'type': response.meta['results_url'],
            'nationality': self.__extract_info(response, "//nav[@class='breadcrumbs']//li[2]/a/text()"),
            'city_name': self.__extract_info(response, "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()"),
            'province_name': self.__extract_info(response, "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()"),
            'country_name': self.__extract_info(response, "//nav[@class='breadcrumbs']//li[3]/a/text()"),
            'name': self.__extract_info(response, "//nav[@class='breadcrumbs']//li[5]/text()"),
            'expiration_date': self.__extract_info(response, "//div[@class='offer']//div[@class='dtable']//p/text()"),
            'functions': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Funciones')]//following-sibling::pre[1]/text()"),
            'requirements': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Requisitos')]//following-sibling::pre[1]/text()"),
            'it_is_offered': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Se ofrece')]//following-sibling::pre[1]/text()"),
            'tags': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Etiquetas')]//following-sibling::ul[@class='tags']/li/text()"),
            'area': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Área')]//following-sibling::p[1]/text()"),
            'category_level': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'ategoría')or contains(text(), 'ivel')]//following-sibling::p[1]/text()"),
            'vacancies': self.__extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Vacantes')]//following-sibling::p[1]/text()"),
            'company_name': self.__get_company_name(response),
            'company_description': self.__extract_info(response, "//div[@class='company']//pre/text()"),
            'company_city_name': self.__extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[child::span]/text()"),
            'company_category': self.__extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[@class='category']/text()"),
            'company_offers': self.__extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[child::a]/a/text()")
        }

        #
        #'company': response.xpath("//div[@class='main-title']//ul[@class='details inline'][1]//li/a/text()").extract_first(),
        # El orden en el que se asignan los valores será su  orden
        #ie = JobItem(ie_dict)
        yield ie_dict

    def __extract_info(self, response, xpath):
        try:
            info = response.xpath(xpath).extract_first()
        except Exception as e:
            print('__extract_info error: %s'%e)
            info = None
        return info

    def __get_company_name(self, response):
        company_name = self.__extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[child::a]/a/text()")
        if not company_name:
            company_name = self.__extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()")
            if not company_name:
                company_name = self.__extract_info(response, "//div[@class='company']//*[@class='title']/text()")
                if not company_name:
                    company_name = '?'
        company_name = company_name.strip()
        if 'importante empresa' in company_name.lower():
            description = self.__extract_info(response, "//div[@class='company']//pre/text()")
            try:
                name = re.split('\.|\n', description)[0]
            except:
                name = None
            if name and ('empresa' in name.lower()) and not(company_name.lower() in name.lower() or name.lower() in company_name.lower()):
                company_name = company_name + ' - ' + name.strip()
        return company_name


    def __get_country(self, response):
        country = response.xpath("//nav[@class='breadcrumbs']//li[3]/a/text()").extract_first()
        if 'Otros Paises' in country:
            country = response.xpath("//div[@class='company']//*[contains(@class,'details')]/li[1]/text()").extract_first()
        return country


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


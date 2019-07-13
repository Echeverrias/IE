# -*- coding: utf-8 -*-
from scrapy.spiders import Spider,CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
from ..items import JobItem, CompanyItem
import math
import re
import random
import time



class InfoempleoSpider(Spider):

    name = 'ie'
    allowed_domains = ['infoempleo.com']

    start_urls = [
        "https://www.infoempleo.com/primer-empleo/",
    ]

    start_urls3 = [
        "https://www.infoempleo.com/primer-empleo/",
        "https://www.infoempleo.com/ofertas-internacionales/",
    ]

    start_urls2 = [
                "https://www.infoempleo.com/primer-empleo/",
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
                "https://www.infoempleo.com/trabajo/area-de-empresa_telecomunicaciones/",
                ]


    allowed_hrefs = [
                    "https://www.infoempleo.com/ofertas-internacionales/",
                    "https://www.infoempleo.com/trabajo/",
                    "https://www.infoempleo.com/primer-empleo/",
                    ]


    def parse(self, response):
        print(f'parse {response.url}')
        print(response.url)
        job_urls = response.xpath("//*[@id='main-content']/div[2]/ul/li/h2/a/@href").extract()

        for job_url in job_urls:
            print('# Go to job_url: %s', job_url)
            yield response.follow(job_url, self.parse_item, meta={"results_url": response.url})
            break

        try:
            if self._is_there_next_page(response):
                next_url = self._get_next_page_url(response.url)
                print('#go to next url %s' % next_url) ##
                yield response.follow(next_url, self.parse)
            else:
                print('# All the pages have been parsed')
        except Exception as e:
            print(f'Exception {e}')


    def _is_there_next_page(self, response):
        print('#__is_there_next_page')
        try:
            # results_shower == 'Mostrando 1-20 de 1028 ofertas'
            results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
            text = results_showed.replace('-', ' ')  # Mostrando 1-20 de 1028 ofertas
            numbers = [int(s) for s in text.split() if s.isdigit()]
            return numbers[1] < 20 #numbers[2]
        except:
            try:
                # page_not_found == 'Lo sentimos, hemos rastreado nuestra web y no hemos encontrado la página que buscas.'
                page_not_found = response.xpath("//*[@class='error404']//div[3]/div/text()").extract_first().strip()
                raise Exception(page_not_found )
            except Exception as e:
                print(f'Error trying to find error 404: {e}')
                raise Exception('The page has not loaded correctly')


    def _clean_url(self, url):
        clean_url = url
        try:
            clean_url = re.findall('(.*/)\?pagina=\d+', url)[0]
        except:
            pass
        return clean_url

    def _get_next_page_url(self, url):
        print('* get_next_page_url: %s'%url)
        try:
            href = self._clean_url(url)
            print('href: %s'%href)
            try:
                next_page = int(re.findall(r'\d+', url)[0]) + 1
                print(next_page)
            except:
                next_page = 2
            return f'{href}?pagina={str(next_page)}'
        except Exception as e:
            print('Error getting next page url: %s' % e)
            return url

        
    def parse_item(self, response):
        print('PARSE_ITEM')
        print (response.url)



        company_dict = {
            'company_link': self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li/a/@href"),
            'company_name': self._get_company_name(response),
            'company_description': self._extract_info(response, "//div[@class='company']//pre/text()"),
            'company_city_name': self._extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[child::span]/text()"),
            'company_category': self._extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[@class='category']/text()"),
            'company_offers': self._extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[child::a]/a/text()")
        }

        job_dict = {
            'link': response.url,
            'registered_people': self._extract_info(response, "//div[@class='main-title']//ul[@class='meta']/li/span/text()"),
            'id': self._extract_info(response, "(//div[@class='main-title']//ul[@class='details inline']/li/text())[1]"),
            'job_date': self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/text()"),
            'summary': self._extract_info(response, "//div[@class='main-title']//p/text()"),
            'type': response.meta['results_url'],
            'nationality': self._extract_info(response, "//nav[@class='breadcrumbs']//li[2]/a/text()"),
            'city_name': self._extract_info(response, "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()"),
            'province_name': self._extract_info(response, "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()"),
            'country_name': self._extract_info(response, "//nav[@class='breadcrumbs']//li[3]/a/text()"),
            'name': self._extract_info(response, "//nav[@class='breadcrumbs']//li[5]/text()"),
            'expiration_date': self._extract_info(response, "//div[@class='offer']//div[@class='dtable']//p/text()"),
            'functions': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Funciones')]//following-sibling::pre[1]/text()"),
            'requirements': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Requisitos')]//following-sibling::pre[1]/text()"),
            'it_is_offered': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Se ofrece')]//following-sibling::pre[1]/text()"),
            'tags': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Etiquetas')]//following-sibling::ul[@class='tags']/li/text()"),
            'area': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Área')]//following-sibling::p[1]/text()"),
            'category_level': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'ategoría')or contains(text(), 'ivel')]//following-sibling::p[1]/text()"),
            'vacancies': self._extract_info(response, "//div[@class='offer']//h3[contains(text(), 'Vacantes')]//following-sibling::p[1]/text()"),
        }


        company_item = CompanyItem(company_dict)
        job_item = JobItem(job_dict)
        job_item['company'] = company_item

        yield job_item

    def _extract_info(self, response, xpath):
        try:
            info = response.xpath(xpath).extract_first()
        except Exception as e:
            print('__extract_info error: %s'%e)
            info = None
        return info

    def _get_company_name(self, response):
        company_name = self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[child::a]/a/text()")
        if not company_name:
            company_name = self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()")
            if not company_name:
                company_name = self._extract_info(response, "//div[@class='company']//*[@class='title']/text()")
                if not company_name:
                    company_name = '?'
        company_name = company_name.strip()
        if 'importante empresa' in company_name.lower():
            description = self._extract_info(response, "//div[@class='company']//pre/text()")
            try:
                name = re.split('\.|\n', description)[0]
            except:
                name = None
            if name and ('empresa' in name.lower()) and not(company_name.lower() in name.lower() or name.lower() in company_name.lower()):
                company_name = f'{company_name} - {name.strip()}'
        return company_name


    def _get_country(self, response):
        country = self._extract_info(response, "//nav[@class='breadcrumbs']//li[3]/a/text()")
        if 'Otros Paises' in country:
            country = self._extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[1]/text()")
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


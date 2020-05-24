# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from scrapy import signals, Request
from collections import namedtuple
import re
from ..items import JobItem, CompanyItem
from ..pipelines import CleaningPipeline, StoragePipeline
import ie_scrapy.keys as key
from core.management.commands.initdb import initialize_database
import time
import pickle

# INFO: 197 scraped offers in 20 minutes
# INFO: 67 scraped offers in 1 minute
# INFO: 15000 scraped offers in 4 hours
# INFO: 6 scraped offers in 1 minute

class BaseException(Exception):
    pass

class PageNotFoundError(BaseException):
    pass

class NoExistentPageError(BaseException):
    pass

class NoElementFoundError(BaseException):
    pass


class InfoempleoSpider(Spider):

    name = 'ie'
    allowed_domains = ['infoempleo.com']
    start_urls__ = ["https://www.infoempleo.com/trabajo/area-de-empresa_legal/"]
    start_urls_ = ["https://www.infoempleo.com/trabajo/area-de-empresa_educacion-formacion/"]
    start_urls = [
        "https://www.infoempleo.com/trabajo/area-de-empresa_sanidad-salud-y-servicios-sociales/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_educacion-formacion/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_tecnologia-e-informatica/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_medios-editorial-y-artes-graficas/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_comercial-ventas/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_ingenieria-y-produccion/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_profesionales-artes-y-oficios/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_compras-logistica-y-transporte/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_hosteleria-turismo/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_administracion-de-empresas/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_administrativos-y-secretariado/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_atencion-al-cliente/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_banca-y-seguros/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_calidad-id-prl-y-medio-ambiente/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_construccion-e-inmobiliaria/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_internet/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_legal/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_marketing-y-comunicacion/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_recursos-humanos/",
        "https://www.infoempleo.com/trabajo/area-de-empresa_telecomunicaciones/",
        "https://www.infoempleo.com/ofertas-internacionales/",
        "https://www.infoempleo.com/primer-empleo/",
    ]

    #% Esta variable ya no hace falta
    allowed_hrefs = [
        "https://www.infoempleo.com/ofertas-internacionales/",
        "https://www.infoempleo.com/trabajo/",
        "https://www.infoempleo.com/primer-empleo/",
    ]

    pipelines = set([
        CleaningPipeline,
        StoragePipeline,
    ])

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(InfoempleoSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s', spider.name)
        try:
            initialize_database()
        except Exception as e:
            print(e)

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)

    def parse(self, response):
        start_url = self._clean_url(response.url)
        job_urls = response.xpath("//*[@id='main-content']/div[2]/ul/li/h2/a/@href").extract()
        try:
            total_results =  self._get_the_total_number_of_results(response)
        except Exception as e:
            total_results = 0
        #job_urls = ['https://www.infoempleo.com/ofertasdetrabajo/operarioa-metal/mostoles/2459763/']
        for job_url in job_urls:
            print('# Go to job_url: %s', job_url) #%
            yield response.follow(job_url, self.parse_item, meta={
                key.START_URL: start_url,
                key.TOTAL_RESULTS: total_results,
            })
        try:
            if self._is_there_next_page(response):
                next_url = self._get_next_page_url(response.url)
                print('');
                print('**');
                print(f'* Next page: {next_url}')
                if next_url:
                    yield response.follow(next_url, self.parse)
                else:
                    print(f'* {next_url} has been parsed')
            else:
                print('All the pages have been requested')
        except NoExistentPageError as e:
            print(f'The url {response.url} has not jobs: {e}')

    def _get_info_of_number_of_results(self, response):
        """
        Return from a results page a tuple with the numbers of the first result showed, the last result showed
        and the total of results. 
        """
        try:
            # results_showed == 'Mostrando 1-20 de 1028 ofertas'
            results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
            text = results_showed.replace('-', ' ')
            numbers = [int(s) for s in text.split() if s.isdigit()]
            InfoResults = namedtuple('ResultsNumberInfo',['first_result_showed', 'last_result_showed', key.TOTAL_RESULTS])
            return InfoResults(numbers[0], numbers[1], numbers[2])
        except Exception as e:
            raise NoElementFoundError()


    def _get_the_total_number_of_results(self, response):
        try:
            info_results =  self._get_info_of_number_of_results(response)
            return info_results.total_results
        except NoElementFoundError as e:
            raise NoElementFoundError()

    def _is_there_next_page(self, response):
        try:
            info_results = self._get_info_of_number_of_results(response)
            print(info_results)
            return info_results.last_result_showed < info_results.total_results
        except NoElementFoundError as e:
            raise NoExistentPageError()

    def _clean_url(self, url):
        """
        Return the url without queries

        :param url: url maybe with queries
        :return: url
        """
        clean_url = url
        try:
            clean_url = re.findall('(.*/)\?pagina=\d+', url)[0]
        except:
            pass
        return clean_url

    def _get_next_page_url(self, url, next_page=None):
        href = self._clean_url(url)
        if not next_page:
            try:
                next_page = int(re.findall(r'\d+', url)[0]) + 1
            except: # The current page is the page 1
                next_page = 2
        next_page_url = f'{href}?pagina={str(next_page)}'
        return next_page_url

    def parse_item(self, response):
        company_dict = self._get_company_info(response)
        job_dict = self._get_job_info(response)
        company_item = CompanyItem(company_dict)
        job_item = JobItem(job_dict)
        job_item['company'] = company_item
        _save(company_item, 'company_item.item')
        _save(job_item, 'job_item.item')
        yield job_item

    def _get_company_info(self, response):
        company_dict = {
            'link': self._extract_info(response,
                                       "//div[@class='main-title']//ul[@class='details inline'][1]//li/a/@href"),
            'name': self._get_company_name(response),
            'description': self._get_company_description(response),
            'resume': self._extract_info(response,
                                         "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()"),
            '_location': self._extract_info(response,
                                            "//div[contains(@class,'company')]//*[contains(@class,'details')]/li[child::span]/text()"),
            'category': self._extract_info(response,
                                           "//div[contains(@class,'company')]//*[contains(@class,'details')]/li[@class='category']/text()"),
            'offers': self._extract_info(response,
                                         "//div[@class='company']//*[contains(@class,'details')]/li[child::a]/a/text()")
        }
        _save(company_dict, 'company_info.dict')
        return company_dict

    def _get_job_info(self, response):
        # doesn't support ManyToManyFields
        job_dict = {
            'link': response.url,
            'registered_people': self._extract_info(response,
                                                    "//div[@class='main-title']//ul[@class='meta']/li/span/text()"),
            'id': self._extract_info(response,
                                     "(//div[@class='main-title']//ul[@class='details inline']/li/text())[1]"),
            'state': self._extract_info(response,
                                        "//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/span/text()"),
            'first_publication_date': self._extract_info(response,
                                                         "//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/text()"),
            'last_update_date': self._extract_info(response,
                                                   "//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/text()"),
            '_summary': self._extract_info(response, "//div[@class='main-title']//p/text()"),
            'type': response.meta[key.START_URL],
            'nationality': self._extract_info(response, "//nav[@class='breadcrumbs']//li[2]/a/text()"),
            '_cities': self._extract_info(response,
                                           "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()"),
            '_province': self._extract_info(response,
                                               "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()"),
            '_country': self._extract_info(response,
                                              "//nav[@class='breadcrumbs']//a[contains(text(), 'Empleo')]/text()"),
            'name': self._extract_info(response, "//nav[@class='breadcrumbs']//li[5]/text()"),
            'expiration_date': self._extract_info(response, "//div[@class='offer']//div[@class='dtable']//p/text()"),
            'description': self._extract_info(response, "//div[@class='offer']//h2//following-sibling::p[1]/text()"),
            'functions': self._extract_info(response,
                                            "//div[@class='offer']//h3[contains(text(), 'Funciones')]//following-sibling::pre[1]/text()") or
                         self._extract_info(response,
                                            "//h3[contains(., 'responsabilities') or contains(., 'RESPONSABILITIES')]//following-sibling::pre[1]/pre[1]/text()"),
            'requirements': self._extract_info(response,
                                               "//div[@class='offer']//h3[contains(text(), 'Requisitos')]//following-sibling::pre[1]/text()") or
                            self._extract_info(response,
                                               "//h3[contains(., 'PROFILE') or contains(., 'profile')]//following-sibling::pre[1]/pre[1]/text()"),
            'it_is_offered': self._extract_info(response,
                                                "//div[@class='offer']//h3[contains(text(), 'Se ofrece')]//following-sibling::pre[1]/text()") or
                             self._extract_info(response,
                                                "//h3[contains(., 'OFFER') or contains(., 'offer')]//following-sibling::pre[1]/pre[1]/text()"),
            '_tags': self._extract_info(response,
                                       "//div[@class='offer']//h3[contains(text(), 'Etiquetas')]//following-sibling::ul[@class='tags']/li/text()"),
            'area': self._extract_info(response,
                                       "//div[@class='offer']//h3[contains(text(), 'Área')]//following-sibling::p[1]/text()") or
                    self._extract_info(response, "//nav[@class='breadcrumbs']//a[contains(text(), 'Area')]/text()"),
            'category_level': self._extract_info(response,
                                                 "//div[@class='offer']//h3[contains(text(), 'ategoría')or contains(text(), 'ivel')]//following-sibling::p[1]/text()"),
            'vacancies': self._extract_info(response,
                                            "//div[@class='offer']//h3[contains(text(), 'Vacantes')]//following-sibling::p[1]/text()"),
        }
        _save(job_dict, 'job_info.dict')
        return job_dict

    def _extract_info(self, response, xpath):
        try:
            info = response.xpath(xpath).extract_first() or ''
        except Exception as e:
            info = ''
        return info

    def _get_company_category(self, response):
        # Intentamos obtener la categoría que se muestra de una compañía registrada en infoempleo
        company_category = self._extract_info(response, "//div[@class='company']//*[contains(@class,'details')]/li[@class='category']/text()")
        # Si la compañía no esta registrada tomamos la breve descripción
        if not company_category:
            company_category = self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()")
            company_category = company_category.strip()
            company_category = company_category.replace('.', "") if company_category.endswith('.') else company_category
            # Si la breve descripción es escueta tomamos la descripción completa
            if (
                (company_category.lower() == "importante empresa") or
                (company_category.lower() == "importante empresa en expansión") or
                (company_category.lower() == "empresa líder en su sector")
            ):
                company_category = (
                        self._extract_info(response, "//div[@class='company']//pre/text()") or
                        self._extract_info(response, "//div[@id='content']//pre[1]/text()")
                )
        return company_category

    def _get_company_description(self, response):
        # Si no existe descripción se tomará la breve descripción
        company_description = (
            self._extract_info(response, "//div[contains(@class,'company')]//pre/text()") or
            self._extract_info(response, "//div[contains(@class,'company')]//p/text()") or
            self._extract_info(response, "//div[@id='content']//pre[1]/text()") or
            self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()")
        )
        return company_description

    def _get_company_name(self, response):
        company_name = (
            self._extract_info(response, "//div[contains(@class,'company')]//*[@class='title']/text()") or
            self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[child::a]/a/text()") or
            self._extract_info(response, "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()")
        )
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

def _save(object, file_name):
    with open(file_name, 'wb') as f:
        pickle.dump(object, f)


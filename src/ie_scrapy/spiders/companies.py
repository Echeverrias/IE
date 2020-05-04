# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
import re
import os
from ..items import CompanyItem
from job.init_db import initialize_database
import json #%

class InfoempleoCompaniesSpider(scrapy.Spider):
    name = 'companies'
    allowed_domains = ['infoempleo.com']
    start_urls = ['https://www.infoempleo.com/empresas-colaboradoras/']

    custom_settings = {
        'FEED_URI': 'companies_.json',
        'FEED_FORMAT': "json",
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(InfoempleoCompaniesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
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
        print('PARSE')
        categories_selectors = response.xpath("//div[contains(@id, 'lightbox-subarea')]")
        for company_selector in categories_selectors:
            area = company_selector.xpath(".//header/text()").extract_first()
            companies_selectors = company_selector.xpath(".//li")
            for company_selector in companies_selectors:
                name = company_selector.xpath(".//a/img/@alt").extract_first()
                link = company_selector.xpath(".//a/@href").extract_first()
                link = self._clean_company_url(link)
                if link:
                    print(f'YIELDING: {link}')
                    yield response.follow(link, self.parse_item, meta={'name': name, 'area': area, 'link': link})
                else:
                    company_item = CompanyItem(name=name, area=area, is_registered=True)
                    yield company_item
                break
            break

    def _clean_company_url(self, link):
        if "http" not in link:
            return "https://www.infoempleo.com" + link
        else:
            breakpoint() if ("https://www.infoempleo.com" not in link) else 2+2 #%
            return link

    def parse_item(self, response):
        print(f'PARSE_ITEM: {response.url}')
        if not response.url.startswith("https://www.infoempleo.com"):
            if not response.meta.get('second_request'):
                breakpoint()
                name = response.meta.get('name')
                area = response.meta.get('area')
                link = response.meta.get('redirect_urls')[0]
                print(f'redirect_urls: {response.meta.get("redirect_urls")}')
                with open('redirections.json', 'a') as f:
                    json.dump({'name': name, 'area': area, 'link':link, 'url': response.url}, f)
                yield response.follow(link, self.parse_item, meta={'name': name, 'area': area, 'second_request': True})
            else:
                with open('redirections.json', 'a') as f:
                    json.dump({'name': response.meta.get('name'), 'area': response.meta.get('area'), 'link': response.meta.get('redirect_urls')[0], 'url': response.url}, f)
                breakpoint()
                print(f'redirect_urls: {response.meta.get("redirect_urls")}')
        else:
            company_dict = self._get_company_info(response)
            company_item = CompanyItem(company_dict)
            yield company_item

    def _extract_info(self, response, xpath):
        try:
            info = response.xpath(xpath).extract_first() or ''
        except Exception as e:
            print('__extract_info error: %s'%e)
            info = ''#None
        return info

    def _get_company_info(self, response):
        company_dict = {
            'link': response.url,
            'name': self._get_company_name(response) or response.meta['name'],
            'reference': self._get_company_reference(response),
            'is_registered': True,
            'area': response.meta['area'],
            'description': self._get_company_description(response),
            'resume': self._extract_info(response,
                                         "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()"),
            '_location': self._extract_info(response,
                                            "//div[contains(@class,'company')]//*[contains(@class,'details')]/li[child::span]/text()"),
            'category': self._extract_info(response,
                                           "//div[contains(@class,'company')]//*[contains(@class,'details')]/li[@class='category']/text()"),
            'offers': (self._extract_info(response,
                                         "//div[contains(@class, 'company')]//*[contains(@class,'details')]/li[child::a]/a/text()") or
                       self._extract_info(response, "//section//p[contains(@class,'h1')]/text()"))
        }
        return company_dict

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
                self._extract_info(response,
                                   "//div[@class='main-title']//ul[@class='details inline'][1]//li[child::a]/a/text()") or
                self._extract_info(response,
                                   "//div[@class='main-title']//ul[@class='details inline'][1]//li[2]/text()")
        )
        company_name = company_name.strip()
        if 'importante empresa' in company_name.lower():
            description = self._extract_info(response, "//div[@class='company']//pre/text()")
            try:
                name = re.split('\.|\n', description)[0]
            except:
                name = None
            if name and ('empresa' in name.lower()) and not (
                    company_name.lower() in name.lower() or name.lower() in company_name.lower()):
                company_name = f'{company_name} - {name.strip()}'
        return company_name

    def _get_company_reference(self, response):
        link = response.url
        reference = os.path.basename(os.path.dirname(link))
        reference = reference if reference.isnumeric() else None
        return reference
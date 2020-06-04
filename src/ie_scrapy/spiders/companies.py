# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
import re
import os
from ..items import CompanyItem
import logging
logging.getLogger().setLevel(logging.INFO)

class InfoempleoCompaniesSpider(scrapy.Spider):
    name = 'companies'
    allowed_domains = ['infoempleo.com']
    start_urls = ['https://www.infoempleo.com/empresas-colaboradoras/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(InfoempleoCompaniesSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        return spider

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s', spider.name)

    def spider_closed(self, spider):
        spider.logger.info('Spider closed: %s', spider.name)

    def parse(self, response):
        categories_selectors = response.xpath("//div[contains(@id, 'lightbox-subarea')]")
        for company_selector in categories_selectors:
            area = company_selector.xpath(".//header/text()").extract_first()
            companies_selectors = company_selector.xpath(".//li")
            for company_selector in companies_selectors:
                name = company_selector.xpath(".//a/img/@alt").extract_first()
                link = company_selector.xpath(".//a/@href").extract_first()
                link = self._clean_company_url(link)
                if link:
                    yield response.follow(link, self.parse_item, meta={'name': name, 'area': area, 'link': link, 'is_registered': True})
                else:
                    company_item = CompanyItem(name=name, area=area, is_registered=True)
                    yield company_item

    def _clean_company_url(self, link):
        domain = "https://www.infoempleo.com"
        if link == '/' or link == f'{domain}/':
            return None
        elif 'https' not in link:
            return domain + link
        elif "https://www.infoempleo.com" not in link:
            return None
        else:
            return link

    def parse_item(self, response):
        company_dict = self._get_company_info(response)
        company_item = CompanyItem(company_dict)
        yield company_item

    def _extract_info(self, response, xpath):
        try:
            info = response.xpath(xpath).extract_first() or ''
        except Exception as e:
            logging.error(f'Error: __extract_info error: {e}')
            info = ''
        return info

    def _get_company_info(self, response):
        company_dict = {
            'link': response.url,
            'name': self._get_company_name(response) or response.meta['name'],
            'reference': response.url,
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
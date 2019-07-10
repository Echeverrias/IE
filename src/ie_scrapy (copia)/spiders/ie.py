# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import JobItem
import re


class IeSpider(CrawlSpider):
    name = 'ie'
    allowed_domains = ['infoempleo.com']
    start_urls = ['https://www.infoempleo.com/ofertas-internacionales/']
    """
    start_urls = ['https://www.infoempleo.com/ofertas-internacionales/',
                  "https://www.infoempleo.com/trabajo/"]
    """
    rules = (
        Rule(
            LinkExtractor(allow=(r'https://www.infoempleo.com/ofertasdetrabajo/.'),
                          restrict_xpaths=("//*[@id='main-content']/div[2]/ul/li/h2/a")),
            callback="parse_item"),
    )

    def parse_start_url(self, response):
        print("*****************************************************")
        print("do something with the start url")
        return self.parse_page(response)

    def parse_page(self, response):
        print('PARSE')
        print(response.url)
        """
        if self.__is_there_next_page(response):
            next_url = self.__get_next_page_url(response)
            print('go to next url %s' % next_url) ##
            yield response.follow(next_url, self.parse)
        """

    def __is_there_next_page(self, response):
        print('__is_there_next_page')
        results_showed = response.xpath("//p[contains(text(),'Mostrando')]/text()").extract_first()
        text = results_showed.replace('-', ' ')  # Mostrando 1-20 de 1028 ofertas
        print  ##
        print(text)
        print  ##
        numbers = [int(s) for s in text.split() if s.isdigit()]
        # return numbers[1] < numbers[2]
        return numbers[1] >= 40

    def __get_next_page_url(self, response):
        actual_url = response.url
        try:
            init_url = re.findall(self.start_urls[0] + '|' + self.start_urls[1], actual_url)[0]
            try:
                next_page = int(re.findall(r'\d+', actual_url)[0]) + 1
            except:
                next_page = 2
            return init_url + str(next_page) + '/'
        except Exception as e:
            print('Error getting next page url: %s' % e)
            return actual_url

    def parse_item(self, response):
        print('PARSE_ITEM')
        print(response.url)

        link = response.url
        subscribers = response.xpath("//div[@class='main-title']//ul[@class='meta']/li/span/text()").extract_first()
        _id = response.xpath("(//div[@class='main-title']//ul[@class='details inline']/li/text())[1]").extract_first()
        company = response.xpath(
            "//div[@class='main-title']//ul[@class='details inline'][1]//li/a/text()").extract_first()
        company_link = response.xpath(
            "//div[@class='main-title']//ul[@class='details inline'][1]//li/a/@href").extract_first()
        job_date = response.xpath(
            "//div[@class='main-title']//ul[@class='details inline'][2]//li[2]/text()").extract_first()
        requisites = response.xpath("//div[@class='main-title']//p/text()").extract_first()
        nationality = response.xpath("//nav[@class='breadcrumbs']//li[2]/a/text()").extract_first()
        area = response.xpath("//nav[@class='breadcrumbs']//li[4]/a/text()").extract_first()
        city = response.xpath(
            "//div[@class='main-title']//ul[contains(@class,'details')][2]/li[1]/text()").extract_first()
        country = response.xpath("//nav[@class='breadcrumbs']//li[3]/a/text()").extract_first()
        name = response.xpath("//nav[@class='breadcrumbs']//li[5]/text()").extract_first()

        # El orden en el que se asignan los valores será su  orden
        ie = JobItem()
        ie['_id'] = _id
        ie['name'] = name
        ie['link'] = link
        ie['company_id'] = company_link
        ie['area'] = area
        ie['requisites'] = requisites
        ie['city'] = city
        ie['country'] = country
        ie['nationality'] = nationality
        ie['subscribers'] = subscribers
        ie['job_date'] = job_date

        yield ie

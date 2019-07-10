# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class IeItem(Item):

    def tuple_of_values(self):
        return tuple(self.values())

    def list_of_values(self):
        return list(self.values())

    def list_of_keys(self):
        return list(self.keys())

    def tuple_of_keys(self):
        return tuple(self.keys())

    def get_dict(self):
        return dict(self.items())

    def get_list_of_tuples(self):
        return list(self.items())

    def get_name(self):
        return self.__class.__name__


class CompanyItem(IeItem):
    _id = Field()
    link = Field()
    name = Field()
    city = Field()
    category = Field()
    description = Field()
    vacancies = Field()

    def get_name(self):
        return 'CompanyItem'


class JobItem(IeItem):
    _id = Field()
    name = Field()
    link = Field()
    company_id = Field()
    # description = Field()
    area = Field()
    requisites = Field()  # % cambiar nombre
    city = Field()
    country = Field()
    nationality = Field()
    subscribers = Field()
    job_date = Field()

    def get_name(self):
        return 'JobItem'

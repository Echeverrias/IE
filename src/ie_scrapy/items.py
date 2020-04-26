# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy_djangoitem import DjangoItem
import copy
from job.models import Job, Company, Language, Country, City


class BaseItem(DjangoItem):

    def get_dict(self):
        return dict(self.items())

    def get_dict_deepcopy(self):
        return copy.deepcopy(self.get_dict())

    def get_model_name(self):
        return self.django_model.__name__


class CompanyItem(BaseItem):

    django_model = Company
    _location = Field()



# Doesn't support ManyToManyFields
class JobItem(BaseItem):

    django_model = Job
    _languages = Field()
    """
    _summary = Field()
    _cities = Field()
    _province = Field()
    _country = Field()
"""
    """
    # % Remove from the model:
    _experience = Field()
    _salary = Field()
    _working_day = Field()
    _contract = Field()
    """


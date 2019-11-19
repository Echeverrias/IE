# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy_djangoitem import DjangoItem
from job.models import Job, Company, Language, Country, City
import copy
from django.forms.models import model_to_dict



class BaseItem(DjangoItem):

    def tuple_of_values(self):
        return tuple(self.values())

    def list_of_values(self):
        return list(self.values())

    def list_of_keys(self):
        return list(self.keys())

    def tuple_of_keys(self):
        return tuple(self.keys())

    def get_list_of_tuples(self):
        return list(self.items())

    def get_name(self):
        return self.__class.__name__

    def get_dict(self):
        return dict(self.items())

    def get_dict_deepcopy(self):
        return copy.deepcopy(self.get_dict())


class CompanyItem(BaseItem):

    django_model = Company

    def get_model_name(self):
        return self.django_model.__name__


# doesn't support ManyToManyFields
class JobItem(BaseItem):

    django_model = Job
    #languages = Field()
    def get_model_name(self):
        return self.django_model.__name__

class LanguageItem(BaseItem):

    django_model = Language
    #languages = Field()
    def get_model_name(self):
        return self.django_model.__name__

class CountryItem(BaseItem):

    django_model = Country
    #languages = Field()
    def get_model_name(self):
        return self.django_model.__name__


class CityItem(BaseItem):

    django_model = City
    #languages = Field()
    def get_model_name(self):
        return self.django_model.__name_dict_
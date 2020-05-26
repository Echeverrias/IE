# -*- coding: utf-8 -*-

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
    _location = Field() # optional


# Items don't support ManyToMany Fields
class JobItem(BaseItem):

    django_model = Job
    _languages = Field() # ManyToMany field of the model
    _summary = Field()
    _tags = Field()
    _cities = Field() # ManyToMany field of the model
    _province = Field()
    _country = Field()

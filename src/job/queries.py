##from .models import Job
from django.db import models
from django.db.models import Q, F
from datetime import date

class JobQuerySet(models.QuerySet):

    def nationals(self):
        return self.filter(cities__country__name='España')

    def internationals(self):
        return self.exclude(cities__country__name='España')

    def exclude_first_job(self):
        return self.exclude(type='primer empleo')

    def exclude_not_salary(self):
        return self.exclude(minimum_salary=0)

    def exclude_expirated_offers(self):
        return self.exclude(expiration_date__lt=date.today())

    def annotate_location(self):
        return self.annotate(city_name=F('cities__name'), province_name=F('cities__province__name'), country_name=F('cities__country__name'))

    def annotate_mean_salary(self):
        return self.annotate(mean_salary=(F('minimum_salary') + F('maximum_salary')) / 2)




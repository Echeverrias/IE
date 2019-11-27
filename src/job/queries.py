##from .models import Job
from django.db import models
from django.db.models import Q, F
from datetime import date

STATE_CREATED_JOB = 'Nueva'
STATE_UPDATED_JOB = 'Actualizada'
STATE_CLOSED_JOB = 'Inscripción cerrada'

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
        return self.exclude(state=STATE_CLOSED_JOB).exclude(expiration_date__lt=date.today())

    def annotate_location(self):
        return self.annotate(city_name=F('cities__name'), province_name=F('cities__province__name'), country_name=F('cities__country__name'))

    def annotate_mean_salary(self):
        return self.annotate(mean_salary=(F('minimum_salary') + F('maximum_salary')) / 2)

    def closed_offers(self):
        return self.filter(state=STATE_CLOSED_JOB, expiration_date__lt=date.today())

    def available_offers(self):
        print('qs.available_offers')
        return self.exclude(state=STATE_CLOSED_JOB).exclude(expiration_date__lt=date.today())

    def new_offers(self):
        return self.filter(state=STATE_CREATED_JOB)

    def free_vacancies(self):
        return self.filter(vacancies__gt=F('registered_people'))

    def not_free_vacancies(self):
        return self.filter(vacancies__lte=F('registered_people'))



##from .models import Job
from django.db import models
from django.db.models import Q, F
from django.utils import timezone
from datetime import date, datetime, timedelta


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
        return self.exclude(minimum_salary=0).exclude(minimum_salary=None)

    def exclude_expirated_offers(self):
        return self.exclude(state=STATE_CLOSED_JOB).exclude(expiration_date__lt=date.today())

    def annotate_location(self):
        return self.annotate(city_name=F('cities__name'), province_name=F('cities__province__name'), country_name=F('cities__country__name'))

    def annotate_mean_salary(self):
        return self.annotate(mean_salary=(F('minimum_salary') + F('maximum_salary')) / 2)

    def closed_offers(self):
        return self.filter(state=STATE_CLOSED_JOB, expiration_date__lt=date.today())

    def available_offers(self):
        return self.exclude(state=STATE_CLOSED_JOB).exclude(expiration_date__lt=date.today())

    def new_offers(self):
        return self.filter(state=STATE_CREATED_JOB)

    def free_vacancies(self):
        return self.filter(vacancies__gt=F('registered_people'))

    def not_free_vacancies(self):
        return self.filter(vacancies__lte=F('registered_people'))

    def registered_timedelta_ago(self, timedeltadict):
        try:
            today = timezone.now()
            td = timedelta(**timedeltadict)
            dt = today - td
            return self.filter(created_at__gte=dt)
        except:
            return self.none()

    def modified_timedelta_ago(self, timedeltadict):
        try:
            today = timezone.now()
            td = timedelta(**timedeltadict)
            dt = today - td
            return self.filter(updated_at__gte=dt)
        except:
            return self.none()

    def registered_or_modified_timedelta_ago(self, timedeltadict):
        try:
            today = timezone.now()
            td = timedelta(**timedeltadict)
            dt = today - td
            return self.filter(Q(created_at__gte=dt) | Q(updated_at__gte=dt))
        except:
            return self.none()

    def registered_or_modified_after(self, tz):
        try:
            return self.filter(Q(created_at__gte=tz) | Q(updated_at__gte=tz))
        except:
            return self.none()

    def first_publication_date_timedelta_ago(self, timedeltadict):
        try:
            today = datetime.today()
            td = timedelta(**timedeltadict)
            dt = today - td
            return self.filter(first_publication_date__gte=dt)
        except:
            return self.none()

    def last_updated_date_timedelta_ago(self, timedeltadict):
        try:
            today = datetime.today()
            td = timedelta(**timedeltadict)
            dt = today - td
            return self.filter(last_updated_date__gte=dt)
        except:
            return self.none()

    def first_publication_or_updated_timedelta_ago(self, timedeltadict):
        try:
            today = datetime.today()
            td = timedelta(**timedeltadict)
            dt = today - td
            return self.available_offers().filter(Q(first_publication_date__gte=dt) | Q(last_updated_date__gte=dt)).available_offers()
        except:
            return self.none()

    def availables_in_year(self, year):
        return self.filter(
            Q(first_publication_date__year=year) |
            Q(last_updated_date__year=year)  |
            Q(expiration_date__year=year)).exclude(
                Q(state=STATE_CLOSED_JOB) &
                Q(updated_at__year__lt=year))

    def first_publication_date_in_year(self, year):
        return self.filter(first_publication_date__year=year)

    def first_publication_date_in_month(self, month):
        return self.filter(first_publication_date__month=month)

    def first_publication_date_in_year_range(self, start_year, end_year):
        return self.filter(first_publication_date__year__range=(start_year, end_year))

    def _first_publication_date_in_month_range_(self, start_month, end_month):
        return self.filter(first_publication_date__month__range=(start_month, end_month))



class CompanyQuerySet(models.QuerySet):

    pass



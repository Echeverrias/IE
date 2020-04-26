from django.db import models
from django.db.models import F
from .queries import JobQuerySet, CompanyQuerySet
from datetime import date


"""
https://medium.com/@jairvercosa/manger-vs-query-sets-in-django-e9af7ed744e0
https://docs.djangoproject.com/en/2.2/topics/db/managers/
"""
class JobManager(models.Manager):


    def get_queryset(self):
        # Don't apply filters here, don't return a modified queryset
        return JobQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints
        )

    def nationals(self):
        return self.get_queryset().nationals()

    def internationals(self):
        return self.get_queryset().internationals()

    def exclude_first_job(self):
        return self.get_queryset().exclude_first_job()

    def exclude_not_salary(self):
        return self.get_queryset().exclude_not_salary()

    def exclude_expirated_offers(self):
        return self.get_queryset().exclude_expirated_offers()

    def annotate_location(self):
        return self.get_queryset().annotate_location()

    def annotate_mean_salary(self):
        return self.get_queryset().annotate_mean_salary()

    def closed_offers(self):
        return self.get_queryset().closed_offers()

    def available_offers(self):
        return self.get_queryset().available_offers()

    def new_offers(self):
        return self.get_queryset().new_offers()

    def free_vacancies(self):
        return self.get_queryset().free_vacancies()

    def not_free_vacancies(self):
        return self.get_queryset().not_free_vacancies()

    def registered_timedelta_ago(self, timedeltadict):
        return self.get_queryset().registered_timedelta_ago(timedeltadict)

    def modified_timedelta_ago(self, timedeltadict):
        return self.get_queryset().modified_timedelta_ago(timedeltadict)

    def registered_or_modified_timedelta_ago(self, timedeltadict):
        return self.get_queryset().registered_or_modified_timedelta_ago(timedeltadict)

    def registered_or_modified_after(self, tz):
        return self.get_queryset().registered_or_modified_after(tz)

    def first_publication_date_timedelta_ago(self, timedeltadict):
        return self.get_queryset().first_publication_date_timedelta_ago(timedeltadict)

    def last_updated_date_timedelta_ago(self, timedeltadict):
        return self.get_queryset().last_updated_date_timedelta_ago(timedeltadict)

    def first_publication_or_updated_timedelta_ago(self, timedeltadict):
        return self.get_queryset().first_publication_or_updated_timedelta_ago(timedeltadict)

    def availables_in_year(self, year):
        return self.get_queryset().availables_in_year(year)

    def first_publication_date_in_year(self, year):
        return self.get_queryset().first_publication_date_in_year(year)

    def first_publication_date_in_month(self, month):
        return self.get_queryset().first_publication_date_in_month(month)


class CompanyManager(models.Manager):

    def get_queryset(self):
        # Don't apply filters here, don't return a modified queryset
        return CompanyQuerySet(
            model=self.model,
            using=self._db,
            hints=self._hints
        )

    def registered_companies(self):
        return self.get_queryset().registered_companies()

from django.db import models
from django.db.models import F
from .queries import JobQuerySet
from datetime import date


"""
https://medium.com/@jairvercosa/manger-vs-query-sets-in-django-e9af7ed744e0
https://docs.djangoproject.com/en/2.2/topics/db/managers/
"""
class JobManager(models.Manager):


    def get_queryset(self):

        # Don't apply filters, don't return a modified queryset
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

    def free_vacancies(self):
        return self.get_queryset().free_vacancies()

    def not_free_vacancies(self):
        return self.get_queryset().not_free_vacancies()


from django.test import TestCase
from job.filters import JobFilter
from job.models import Job, Company
import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta



class JobFilterTest(TestCase):

   @classmethod
   def setUpTestData(cls):
      """
      free vacancies jobs: 4
      available_jobs: 5

      """
      cls.key = 'madrid'
      company_key = Company.objects.create(name=cls.key)
      Job.objects.create(id=1, name=cls.key, vacancies=1)
      Job.objects.create(id=2, functions=cls.key + " - ...", vacancies=1)
      Job.objects.create(id=3, requirements=cls.key, vacancies=2, registered_people=1)
      Job.objects.create(id=4, it_is_offered=cls.key, vacancies=5, registered_people=23)
      Job.objects.create(id=5, company=company_key, vacancies=5, registered_people=10)
      Job.objects.create(id=6, company=company_key, vacancies=5, registered_people=10)
      #  Not available jobs:
      now = timezone.now()
      rel = relativedelta(days=5)
      yesterday = now - rel
      Job.objects.create(id=7, name=cls.key, expiration_date=yesterday)
      Job.objects.create(id=8, functions="x", state=Job.STATE_CLOSED)

   def test_get_all_jobs(self):
      filter = JobFilter()
      self.assertEqual(filter.qs.count(), 8)

   def test_get_available_jobs_by_text_field(self):
      filter_data = {
            'text': self.key,
         }
      filter = JobFilter(filter_data)
      self.assertEqual(filter.qs.count(), 7)

   def test_get_available_jobs_by_free_vacancies(self):
      filter_data = {
         'free_vacancies': True,
      }
      filter = JobFilter(filter_data)
      self.assertEqual(filter.qs.count(), 3)
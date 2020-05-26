from django.test import TestCase
from job.models import Job, Company, City, Province, Country, Community, Language
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class TestJobManager(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.today = timezone.now()
        rel = relativedelta(days=1)
        cls.yesterday = cls.today - rel

    def test_available_offers(self):
        Job.objects.create(id=4, vacancies=5, registered_people=10)
        Job.objects.create(id=5, vacancies=5, registered_people=10)
        Job.objects.create(id=6, vacancies=5, registered_people=10)
        Job.objects.create(id=7, name='', expiration_date=self.yesterday)
        Job.objects.create(id=8, functions="x", state=Job.STATE_CLOSED)
        self.assertEqual(Job.objects.available_offers().count(), 3)

    def test_exclude_expirated_offers(self):
        Job.objects.create(id=4, vacancies=5, registered_people=10)
        Job.objects.create(id=5, vacancies=5, registered_people=10)
        Job.objects.create(id=6, vacancies=5, registered_people=10)
        Job.objects.create(id=7, name='', expiration_date=self.yesterday)
        Job.objects.create(id=8, functions="x", state=Job.STATE_CLOSED)
        self.assertEqual(Job.objects.exclude_expirated_offers().count(), 3)

    def test_annotate_location(self):
        country = Country.objects.create(name="España")
        province = Province.objects.create(id=1, name="Almería")
        city = City.objects.create(name="Somontín")
        city.country = country
        city.province = province
        city.save()
        job = Job.objects.create(id=1, name='test', country=country, province=province)
        job.cities.add(city)
        job = Job.objects.annotate_location().get(id=1)
        self.assertEqual(job.country_name, 'España')
        self.assertEqual(job.province_name, 'Almería')
        self.assertEqual(job.city_name, 'Somontín')
        country = Country.objects.create(name="Alemanía")
        city = City.objects.create(name="Berlín")
        city.country = country
        city.save()
        job = Job.objects.create(id=2, name='test', country=country)
        job.cities.add(city)
        job = Job.objects.annotate_location().get(id=2)
        self.assertEqual(job.country_name, 'Alemanía')
        self.assertIsNone(job.province_name)
        self.assertEqual(job.city_name, 'Berlín')

    def test_annotate_mean_salary(self):
        Job.objects.create(id=1, name='test', minimum_salary=1000, maximum_salary=2000)
        Job.objects.create(id=2, name='test')
        qs = Job.objects.all().annotate_mean_salary()
        self.assertEqual(qs.get(id=1).mean_salary, 1500)
        self.assertEqual(qs.get(id=2).mean_salary, None)

    def test_free_vacancies(self):
        Job.objects.create(id=1, name='test', vacancies=23)
        Job.objects.create(id=2, name='test', vacancies=23, registered_people=23)
        Job.objects.create(id=3, name='test', vacancies=23, registered_people=33)
        qs = Job.objects.free_vacancies()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].id, 1)

    def test_registered_timedelta_ago(self):
        three_days_ago = self.today - relativedelta(3)
        five_days_ago = self.today - relativedelta(5)
        Job.objects.create(id=1)
        Job.objects.create(id=2)
        Job.objects.filter(id=1).update(created_at=five_days_ago)
        Job.objects.filter(id=2).update(created_at=three_days_ago)
        qs = Job.objects.registered_timedelta_ago(relativedelta(3))
        try:
            exception = None
            self.assertIsNotNone(qs.get(id=2))
        except Exception as e:
            exception = e
        finally:
            self.assertIsNotNone(exception)

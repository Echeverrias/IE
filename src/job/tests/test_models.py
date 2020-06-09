from django.test import TestCase
from job.models import Job, Company, City, Province, Country, Community, Language
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class TestJob(TestCase):

    @classmethod
    def setUpTestData(cls):
        Job.objects.create(id=555, name="test")
        Job.objects.create(id=777, name="test")
        cls.cities = []
        for i in range(0,2):
            cls.cities.append(City.objects.create(name=str(i)))

    def test_create_timestamp(self):
        now = timezone.now()
        job = Job.objects.get(id=555)
        self.assertEqual(job.created_at.date(), now.date())
        self.assertEqual(job.checked_at.date(), now.date())
        self.assertEqual(job.updated_at, None)
        # If the job has a modification the same day tha it has been created the updated_at field will no update
        job.name = str(now)
        job.save()
        job = Job.objects.get(id=555)
        self.assertEqual(job.updated_at, None)

    def test_update_timestamp(self):
        now = timezone.now()
        yesterday = now - relativedelta(days=1)
        Job.objects.filter(id=555).update(created_at=yesterday, checked_at=yesterday)
        job = Job.objects.get(id=555)
        job.name = str(now)
        job.save()
        job = Job.objects.get(id=555)
        self.assertEqual(job.checked_at.date(), now.date())
        self.assertEqual(job.updated_at.date(), now.date())

    def test_add_cities(self):
        job = Job.objects.get(id=555)
        for city in self.cities:
            job.cities.add(city)
        self.assertEqual(Job.objects.filter(id=555).count(), 1)
        self.assertEqual(Job.objects.get(id=555).cities.all().count(), len(self.cities))

    def test_add_cities_method(self):
        job = Job.objects.get(id=777)
        for city in self.cities:
            Job.add_city(job, city)
        self.assertEqual(Job.objects.filter(id=777).count(), 1)
        self.assertEqual(Job.objects.get(id=777).cities.all().count(), len(self.cities))


class TestCompany(TestCase):

    @classmethod
    def setUpTestData(cls):
        Company.objects.create(name="test", reference=555, link="https://www.infoempleo.com/ofertasempresa/test/555/")
        cls

    def test_create_timestamp(self):
        now = timezone.now()
        company = Company.objects.get(name='test')
        self.assertEqual(company.created_at.date(), now.date())
        self.assertEqual(company.checked_at.date(), now.date())
        self.assertEqual(company.updated_at, None)
        # If the job has a modification the same day tha it has been created the updated_at field will no update
        company.description = str(now)
        company.save()
        company = Company.objects.get(name='test')
        self.assertEqual(company.updated_at, None)

    def test_update_timestamp(self):
        now = timezone.now()
        yesterday = now - relativedelta(days=1)
        Company.objects.filter(name='test').update(created_at=yesterday, checked_at=yesterday)
        company = Company.objects.get(name='test')
        company.description = str(now)
        company.save()
        self.assertEqual(company.checked_at.date(), now.date())
        self.assertEqual(company.updated_at.date(), now.date())

    def test_slug_with_name(self):
        company = Company.objects.create(name="with name", reference=2, link="https://www.infoempleo.com/ofertasempresa/with-name/2/")
        self.assertEqual(company.slug, 'with-name')

    def test_slug_with_link(self):
        company = Company.objects.create(reference=3, link="https://www.infoempleo.com/ofertasempresa/with-link/3/")
        self.assertEqual(company.slug, 'with-link')

    def test_slug_with_id(self):
        company = Company(name='', description="without name and without link")
        company.save()
        self.assertEqual(company.slug, str(company.id))

    def test_get_slug_from_link(self):
        c = Company()
        slug = c._get_slug_from_link()
        self.assertEqual(slug, '')
        c = Company( link = "https://www.infoempleo.com/ofertasempresa/with-link/3/")
        slug = c._get_slug_from_link()
        self.assertEqual(slug, 'with-link')
        c = Company(link = "https://www.infoempleo.com/ofertasempresa/with-link/3")
        slug = c._get_slug_from_link()
        self.assertEqual(slug, 'with-link')



from django.test import TestCase
from job.models import Job, City
# Create your tests here.


def test1():
    # Añade varias ciudades a un trabajo para ver si se duplica o no
    RESULT_EXPECTED = 1

    City.objects.filter(name='xxx').delete()
    City.objects.filter(name='yyy').delete()
    Job.objects.filter(id=555).delete()

    j, is_new = Job.objects.get_or_create(id=555, defaults={'name': '555', 'vacancies': 555})
    c1, is_new = City.objects.get_or_create(name='xxx')
    c2, is_new = City.objects.get_or_create(name='yyy')
    j.cities.add(c1)
    j.cities.add(c2)

    result = Job.objects.filter(id=555).count()

    City.objects.filter(name='xxx').delete()
    City.objects.filter(name='yyy').delete()
    Job.objects.filter(id=555).delete()

    return RESULT_EXPECTED == result

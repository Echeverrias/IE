from django.test import TestCase
from job.models import Job, City
# Create your tests here.
from datetime import date

earliest_updated_job = {
    'state': 'Actualizada',
    'last_updated_date':date(2019,8,5),
    'link': 'https://www.infoempleo.com/ofertasdetrabajo/practicas-titulados-grado-ingenieria-informatica-hm/palencia/2347061/',
}
earliest_updated_job2 = {
    'state': 'Actualizada',
    'last_updated_date':date(2019,8,7),
    'expiration_date':date(2020,2,1),
    'link':  'https://www.infoempleo.com/ofertasdetrabajo/agente-exclusivo-sucursal-de-barcelona/barcelona/1615773/',
}

earliest_cretaed_job = {
    'state': 'Nueva',
    'last_updated_date': date(2019,11,12),
    'link': 'https://www.infoempleo.com/ofertasdetrabajo/beca-tecnico-de-recursos-humanos-generalista/madrid/2567930/',
    'expiration_date': date(2019,12,12),
}

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

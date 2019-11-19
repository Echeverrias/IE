import selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.proxy import Proxy, ProxyType

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from time import sleep
import random

from django.db.models import Q

"""
driver = webdriver.Chrome('chromedriver')
driver.get('https://free-proxy-list.net/anonymous-proxy.html')
driver.execute_script("window.scrollBy(0, %i);"%random.randint(1,150))
"""

from jobs.models import Job, Country, City

def yyy():
    qs = Job.objects.all()
    s = set()
    for j in qs:
        try:
            s.add(j.country.name)
        except:
            print(f'Error: {j.link}')

    for j in s:
        print(j)

    print()
    print()

    qs = City.objects.all()
    ss = set()
    for j in qs:
        try:
            ss.add(j.country.name)
        except:
            print(f'Error: {j.name}')

    for j in ss:
        print(j)

    print()
    print()

def yy_():
    qs = Job.objects.all()
    for j in qs:
        if not j.country:
            print('NOT COUNTRY')
            print(j.link)
            print()
        elif j.country.name.lower().find('empleo') >= 0:
            print(j.link)
            c_ = j.country.name.lower().replace('empleo en ', "")
            try:
                country = Country.objects.filter(name=c_)
                print(country)
            except Exception as e:
                print(f'Error, country not found {e}')

    print()
    print()


def yy():
    print('yy')
    qs = Job.objects.all()
    len(qs)
    qs = Country.objects.all()
    len(qs)
    for c in qs:
        if c.name.lower().find('empleo') >= 0:
            print(c.name)
            for j in c.jobs.all():
                print(j.link)
                print(f'job.country.name: {j.country.name}')

            c_ = c.name.replace('Empleo en ', "")
            try:
                print(c_)
                country = Country.objects.filter(name=c_)
                print(country)
            except Exception as e:
                print(f'Error, city not found {e}')
            print()
            print()
            print('--------------------------------------------------------------')
            for c in c.cities.all():
                print(f'city.country.name: {c.country.name}')
                city = City.objects.filter(name=c.name)
                if city:
                    print(f'{c.name} cities: {city}')
                for j in c.jobs.all():
                    print(j.link)
                    print(f'job.country.name: {j.country.name}')
            print()
            print()
            print('--------------------------------------------------------------')
            print('--------------------------------------------------------------')


def fix1():
    """
        Elimina las ciudades con espacios en blanco que no tienen trabajos
    """
    qs_cities = City.objects.all()
    for city in qs_cities:
        right_name = city.name.strip()
        if city.name != right_name:
            jobs = city.jobs.all()
            if not jobs:
                city.delete()
            else:
                print('wrong city')
                right_city = City.objects.filter(name=right_name, country=city.country)
                print(f'name: {right_name}')
                print(f'country: {city.country}')
                print(right_city)
                if right_city and len(right_city) == 0:
                    right_city = right_city[0]
                    city.delete()
                    for job in jobs:
                        job.add(right_city)
                        job.save()


def fix():

    qs_cities = City.objects.all()
    for city in qs_cities:
        if city.name != city.name.strip():
            jobs = city.jobs.all()
            if not jobs:
                city.delete()

def r():
    cc = City.objects.filter(name__icontains='Alredores de Belfast')
    for c in cc:
        print(c.name)
        jobs = c.jobs.all()
        for j in jobs:
            print(j.link)
        print('--------------------')

def p2():
    """
    country = Country.objects.filter(name="España")[0]
    c = City.objects.filter(country=country)
    print(len(c))
    print(c[0])
    """
    jobs = Job.objects.all()
    cities = City.objects.all()
    qs = cities
    for i in qs:
        if i.country and i.country.name.lower().find('empleo') >=0:
            print(i.name)
            print(i.country.name);
            print()
            right_country = i.country.name.replace('Empleo en ', "")
            country = Country.objects.filter(name=right_country)[0]
            i.country = country
            i.save()


def p2():
    cities = City.objects.all()
    for city in cities:
        country = city.country
        province = city.province
        name = city.name
        id = city.id
        similars = City.objects.filter(~Q(id=id) & Q(name=name, province=province, country=country))
        if similars:
            print(city.id, name, country.name)
            print(similars)
            print([i.id for i in similars])
            jobs = set()
            for similar in similars:
                for job in similar.jobs.all():
                    jobs.add(job)
                    job.cities.clear()
                similar.jobs.clear()
                similar.delete()
            for job in jobs:
                city.jobs.add(job)
            city.save()

def p1():
    cities = City.objects.all()
    for city in cities:
        country = city.country
        province = city.province
        name = city.name
        id = city.id
        similars = City.objects.filter(~Q(id=id) & Q(name=name, province=province, country=country))
        if similars:
            print('City: ')
            print(city.id, name, province, country.name)
            print(len(city.jobs.all()), city.jobs.all())
            print()
            print('Similar cities: ')
            print(similars)
            print([i.id for i in similars])
            print()
            print('Jobs: ')
            jobs = set()
            for similar in similars:
                for job in similar.jobs.all():
                    jobs.add(job)
                    for job in jobs:
                        print(job.cities.all())
                similar.jobs.clear()
                similar.name="zzz"
                similar.save()
            print([j.id for j in jobs])
            for job in jobs:
                print(job.cities.all())
                job.cities.add(city)
                job.save()
            print()
            print('City job: ')
            print(len(city.jobs.all()), city.jobs.all())
            print()
            print('--------------------------------------')
            print()

def px():
    qs = Job.objects.filter(~Q(country__name='España'))
    for j in qs:
        j.cities.clear()
        j.delete()
    qs = Country.objects.filter(~Q(name='España'))
    for c in qs:
        c.cities.all().delete()
        c.save()

def px2():
    gb = Country.objects.filter(name="Gran Bretaña")[0]
    print(gb)
    city, is_new_city = City.objects.get_or_create(name='www', country=gb)
    print(city.id, city, is_new_city)
    is_new_city = City.objects.get_or_create(name__iexact='www', country=gb)
    print(city.id, city, is_new_city)
    is_new_city = City.objects.get_or_create(name__iexact='WWW', country=gb)
    print(city.id, city, is_new_city)

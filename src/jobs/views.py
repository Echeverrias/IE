from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Job, Company, Province, City, Community, Country
from .serializers import JobSerializer, CompanySerializer
from django.forms.models import model_to_dict
from django.http import HttpResponse
from .cities import provincies, cities, communities
import re

from django.shortcuts import render

from django.http import HttpResponse
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from ie_scrapy.spiders.ie import InfoempleoSpider
from twisted.internet import reactor
from multiprocessing import Process, Queue
import os, sys


def welcome_view(request):
    return HttpResponse("<h1>Welcome</h1><a href ='/admin/'>Go to Admin</a><br><a href ='/crawl/'>Run crawler</a><br><a href ='/admin/jobs/job/'>Go to Job</a><br><a href ='/admin/jobs/company/'>Go to Company</a><br><a href ='/reset'>Delete all the companies and jobs</a><br><a href ='/insert_locations'>Insert Locations</a><br><a href ='/query'>Execute query</a>")


def run_crawler(request):
    #https://srv.buysellads.com/ads/click/x/GTND42QNC6BDCKQ7CV7LYKQMCYYIC2QJFTAD4Z3JCWSD42QYCYYIVKQKC6BIKKQIF6AI6K3EHJNCLSIZ?segment=placement:techiediariescom;

    def f(q):
        try:
            crawler_settings = get_project_settings()
            runner = CrawlerRunner(crawler_settings)
            deferred = runner.crawl(InfoempleoSpider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        print('result is not None')
        print(result)
    else:
        print('result is  None')
        print(result)
    return HttpResponse("<h1>%Crawler running...</h1><a href='admin/'>Go to admin</a>")


class JobAPIView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class CompanyAPIView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class JobView(APIView):
    queryset = Job.objects.all()

    def get(self, request, format=False):
        data = {}
        count = 1
        for q in self.queryset.all():
            data[str(count)] = model_to_dict(q)
            count += 1

        return Response(data)

class CompanyView(APIView):
    queryset = Company.objects.all()

    def get(self, request, format=False):
        data = {}
        count = 1
        for q in self.queryset.all():
            data[str(count)] = model_to_dict(q)
            count += 1
        return Response(data)

def cleanup_provinces_view(request):
    queryset = Job.objects.all()


    for j in queryset:
        country = j.country
        if country == 'España':
            print((j.city,))
            city = j.city
            province = __get_text_between_parenthesis(city)
            print('province: %s'%province)
            if not province:
                province = city
            else:
                j.city = j.city[0:j.city.find('(')].strip()
                print('city: %s'%j.city)
            j.province = province
            j.save()
            print((j.city,j.province))
            print()

    return HttpResponse("<h1>Clean up of the provinces completed</h1><a href ='/admin/jobs/job'>admin</a> ")


def cleanup_links_view(request):

    queryset = Company.objects.all()
    print(len(queryset))
    print(len(queryset.all()))
    for c in queryset:
    #if c:
        origin = 'https://www.infoempleo.com/'

        link = c.company_link
        if link:
            print('link: %s'%link)
            if not (origin in link):
                print('in')
                c.company_link = origin + link
                c.save()


    return HttpResponse("<h1>Clean up of the companies link completed</h1><a href ='/admin/jobs/company'>admin</a> ")




def __get_text_between_parenthesis(string):
        text = re.search('\(.*?\)', string)
        if text:
            text = text[0]
            text = text[text.find("(") + 1:text.find(")")]
        else:
            text = None
        return text

def insert_provinces():
    # `provincias` (`id`, `slug`, `provincia`, `comunidad_id`, `capital_id`)
    for p in provincies:
        Province.objects.get_or_create(id=p[0], defaults={'slug':p[1], 'name':p[2], 'community_id':p[3], 'capital_id':p[4],})


def insert_cities():

    for c in cities:
        #(`provincia_id`, `municipio`, `id`, `slug`, `latitud`, `longitud`)
        province = Province.objects.get(id=c[0])
        i, created = City.objects.get_or_create(id=c[2], defaults={'slug':c[3], 'name':c[1], 'province':province, 'latitude':c[4], 'longitude':c[5]})
        if created:
            name = i.name
            print(name)
            l = name.split(', ')
            if len(l) == 2:
                i.name = l[1].strip() + ' ' + l[0].strip()
                i.save()





def insert_communities():
    # https://github.com/antonrodin/municipios/blob/master/comunidades.sql
    # `comunidades` (`id`, `slug`, `comunidad`, `capital_id`) VALUES
    for c in communities:
        community, created = Community.objects.get_or_create(id=c[0], slug=c[1], name=c[2], capital_id=c[3])
        if created:
            provincies = Province.objects.filter(community_number=community.id)
            for p in provincies:
                p.community = community
                p.save()




def get_text_between_parenthesis(string):
    try:
        text = re.search('\(.*?\)', string)

        if text:
            text = text[0]
            text = text[text.find("(") + 1:text.find(")")]
        else:
            text = None
    except:
        text = None
    return text

def province_cleanup(string):
    province = get_text_between_parenthesis(string)
    if not province:
        province = string
    return province

def city_cleanup(string):
    city = string
    if '(' in city:
        city = city[0:city.find('(')].strip()
    return city

def cleanup_spain_cities(request):


    jobs = Job.objects.filter(country='España', city=None)

    print('#Jobs number without citry assigned: %i'%len(jobs))
    for job in jobs:

        dc = job.city_name
        city_name = city_cleanup(dc)
        p = province_cleanup(dc)

        cities = City.objects.filter(name__iexact=city_name)
        if cities:
           pass
        else:
            cities = City.objects.filter(name__icontains=city_name)
        if len(cities) == 1:
            job.city = cities[0]
            job.province = cities[0].province.name
            job.save()
            print('save',job.id, job.city, job.province, p)

        elif len(cities) > 1:
            cities = City.objects.filter(name__icontains=city_name + '/')
            if len(cities) == 1:
                job.city = cities[0]
                job.province = cities[0].province.name
                job.save()
                print('save', job.id, job.city, job.province, p)

        elif not cities:
            provinces = Province.objects.filter(name__icontains=city_name)
            if len(provinces) == 1:
                job.city = None
                job.city_name = ""
                job.province = provinces[0].name
                job.save()
                print('save', job.id, job.city, job.province, p)
        else:
            print(job.id, city_name, p)

    jobs = Job.objects.filter(country='España', city=None, city_name="")
    print('Jobs with wrong location: %i'%len(jobs))

def insert_spain_provinces():

    jobs = Job.objects.filter(country='España', province=None)
    for job in jobs:
        province_name = job.province
        provinces = Province.objects.filter(name__iexact=province_name)
        if len(provinces) == 1:
            job.p = provinces[0]
            job.save()
    jobs = Job.objects.filter(country='España', province=None)
    print('Spain jobs without province: %i'%len(jobs))


def insert_countries():
    jobs = Job.objects.all()
    for job in jobs:
        country_name = job.country
        country, is_a_created_country = Country.objects.get_or_create(name=country_name)
        job.c = country
        job.save()




def prueba(country_string, string):
    country_name = country_string
    province_name = province_cleanup(string)
    city_name = city_cleanup(string)
    print(city_name, province_name, country_name)

    country = None
    if country_name:
        country, is_a_new_country = Country.objects.get_or_create(name__iexact=country_name)
    province = None
    city = None
    if country and country.name == 'España':
        try:
            province = Province.objects.filter(name__iexact=province_name)[0]
            print('Province found: %s'%province)
        except:
            print('Province doesnt found')
        # first search with iexact
        if province:
            cities = City.objects.filter(country=country, province=province, name__iexact=city_name)
        else:
            cities = City.objects.filter(country=country, name__iexact=city_name)
        # second search with icontains
        if not cities:
            if province:
                cities = City.objects.filter(country=country, province=province, name__icontains=city_name)
            else:
                cities = City.objects.filter(country=country, name__icontains=city_name)
        print('Cities found: %s'%cities)
        if len(cities) == 1:
            city = cities[0]
            if province:
                city.province = province
                city.save()
        elif province and not cities:
            city = City.objects.create(name=city_name, province=province, country=country)
        else:
            print('Not found %s - %s - %s'%(city_name, province, country))
    else:
         city, is_a_new_city = City.objects.get_or_create(name=city_name, province= province, country=country)
    return city, province, country


def fix_cities():
    jobs = Job.objects.filter(country="España", p=None)
    #jobs = Job.objects.get(city__name__iexact
    for job in jobs:

        city, province, country = prueba(job.country, job.city_name)
        if not country:

            print('Not country!!!: %i' % job.id)
        else:
            job.c = country
            job.p = province
            job.city = city
            job.save()
        print(job.id, city, province, country)

def insert_communities2(country):
    # https://github.com/antonrodin/municipios/blob/master/comunidades.sql
    # `comunidades` (`id`, `slug`, `comunidad`, `capital_id`) VALUES
    for c in communities:
        Community.objects.get_or_create(id=c[0], slug=c[1], name=c[2], capital_id=c[3], country=country)



def insert_provinces2(country):
    # `provincias` (`id`, `slug`, `provincia`, `comunidad_id`, `capital_id`)

    for p in provincies:
        community = Community.objects.get(id=p[3])
        province, created = Province.objects.get_or_create(id=p[0], defaults={'slug':p[1], 'name':p[2], 'capital_id':p[4], 'community':community})



def insert_cities2(country):

    for c in cities:
        #(`provincia_id`, `municipio`, `id`, `slug`, `latitud`, `longitud`)
        province = Province.objects.get(id=c[0])
        i, created = City.objects.get_or_create(id=c[2], defaults={'slug':c[3], 'name':c[1], 'province':province, 'latitude':c[4], 'longitude':c[5], 'country':country})
        if created:
            name = i.name
            print(name)
            l = name.split(', ')
            if len(l) == 2:
                i.name = l[1].strip() + ' ' + l[0].strip()
                i.save()


def set_spain_locations_view(request):
    country, created = Country.objects.get_or_create(name="España")
    print('%i: %s'%(country.id, country))
    insert_communities2(country)
    insert_provinces2(country)
    insert_cities2(country)
    provinces = Province.objects.all()
    for p in provinces:
        p.country = country
        p.save()
    return HttpResponse("<h1>Locations inserted in the DDBB</h1><br><a href ='/admin'>Go to Admin</a> ")



def __get_location(city_name, province_name, country_name):

    print('#Pipeline__get_location: %s %s %s'%(city_name, province_name, country_name))
    country = None
    if country_name:
        country, is_a_new_country = Country.objects.get_or_create(name=country_name)
    print('Country: %s'%country)
    province = None
    city = None
    if country and country.name == 'España':
        try:
            provinces = Province.objects.filter(name__iexact=province_name)
            print('provinces %s'%provinces)
            province = provinces[0]
        except:
            print('Error getting the province')
            # first search with iexact
        if province:
            cities = City.objects.filter(country=country, province=province, name__iexact=city_name)
        else:
            cities = City.objects.filter(country=country, name__iexact=city_name)
            # second search with icontains
        if not cities:
            if province:
                cities = City.objects.filter(country=country, province=province, name__icontains=city_name)
            else:
                cities = City.objects.filter(country=country, name__icontains=city_name)
        if len(cities) == 1:
            city = cities[0]
            if province:
                city.province = province
                city.save()
        elif province and not cities:
            city = City.objects.create(name=city_name, province=province, country=country)
    else:
        city, is_a_new_city = City.objects.get_or_create(name=city_name, province=province, country=country)
    print('return: %s %s %s'%(city, province, country))
    return city, province, country


def delete_companies_and_jobs_view(request):
    companies = Company.objects.all()
    for company in companies:
        company.delete()

    jobs = Job.objects.all()
    for job in jobs:
        job.delete()

    return HttpResponse("<h1>All the companies and jobs habe benn deleted</h1><a href ='/admin'>Go to Admin</a> ")

def get_info():

    jobs = Job.objects.all()
    areas = set()
    contracts = set()
    working_days = set()
    types = set()
    categories = set()
    max_length_functions = 0
    max_length_it_is_offered = 0
    max_length_requirements = 0

    for job in jobs:
        areas.add(job.area)
        contracts.add(job.contract)
        working_days.add(job.working_day)
        types.add(job.type)
        categories.add(job.category_level)
        try:
            if len(job.functions) > max_length_functions:
                max_length_functions = len(job.functions)
        except:
            pass
        try:
            if len(job.requirements) > max_length_requirements:
                max_length_requirements = len(job.requirements)
        except:
            pass
        try:
            if len(job.it_is_offered) > max_length_it_is_offered:
                max_length_it_is_offered = len(job.it_is_offered)
        except:
            pass


    f = open('info.txt', 'w', encoding='utf8')

    f.write('Areas: \n')
    f.write('\n')
    for x in areas:
        f.write('- %s\n'%x)
    f.write('\n')
    f.write('\n')
    f.write('\n')

    f.write('Contratos: \n')
    f.write('\n')
    for x in contracts:
        f.write('- %s\n' % x)
    f.write('\n')
    f.write('\n')
    f.write('\n')

    f.write('Jornadas: \n')
    f.write('\n')
    for x in working_days:
        f.write('- %s\n' % x)
    f.write('\n')
    f.write('\n')
    f.write('\n')

    f.write('Categorias: \n')
    f.write('\n')
    for x in categories:
        f.write('- %s\n' % x)
    f.write('\n')
    f.write('\n')
    f.write('\n')

    f.write('Tipos: \n')
    f.write('\n')
    for x in types:
        f.write('- %s\n' % x)
    f.write('\n')
    f.write('\n')
    f.write('\n')

    f.write('Long max funciones: %i\n'%max_length_functions)
    f.write('Long max requisitos: %i\n'%max_length_requirements)
    f.write('Long max se ofrece: %i\n'%max_length_it_is_offered)

    f.close()




def query_view(request):
    data=None
    data2 = None


    #j = Job.objects.get(id=2502025)
   # print(j.cities.get())
    def get_text_between_parenthesis(string):
        text_list = re.findall('\(([\d\w\s-]+)\)', string)
        return text_list

    def get_text_before_parenthesis(string):
        text = string
        while True:
            try:
                text = re.findall('(.+)\(', text)[0].strip()
            except:
                break
        return text

    def get_a_list(string):
        return re.split(',| y |;|\n', string)

    def __city_cleanup(string):
        city = get_text_before_parenthesis(string)
        parenthesis = get_text_between_parenthesis(string)
        if parenthesis and len(parenthesis[0]) < 4:
            city = parenthesis[0].capitalize() + " " + city
        return city

    def cities_cleanup(string):
        cities = get_a_list(string)
        return [__city_cleanup(city) for city in cities]
    """
    2511261 <QuerySet []> Álava
    2474359
    """

    companies = Company.objects.all()
    for c in companies:
       cities = City.objects.filter(name=c.company_city_name)
       if cities and len(cities) == 1:
           c.company_city = cities[0]
           c.save()


    #Country.objects.create(name=country)
    return HttpResponse("<h1>Query</h1><div>%s</div><div>%s</div><a href ='/admin'>Go to Admin</a> "%(data, data2))



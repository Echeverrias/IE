# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import sqlite3
import datetime
from django.utils import timezone
import copy
from dateutil.relativedelta import relativedelta
from jobs.models import Job, Company, Country, City, Province
from .items import JobItem, CompanyItem
import time


def trace(func):
    def wrapper(*args, **kwargs):
        print("TRACE: calling: {}() with {}, {}").format(func.__name__, args, kwargs)
        func_result = func(*args, **kwargs)
        print("TRACE: {}() returned {}").format(func.__name__, func_result)
        return func_result

    return wrapper


class CleanupPipeline_(object):

    def str_cleanup(self, string):
        print('#str_cleanup: %s'%string)
        try:
            clean_string = string.strip()
        except Exception as e:
            print('#Error in str_cleanup in %s: %s'%(string, e))
        return clean_string

    def list_cleanup(self, some_list):
        return list(map(lambda e: e.strip(), some_list))

    def str_int_cleanup(self, string):
        try:
            return re.findall(r'\d+', string)[0]
        except:
            return None

    def int_cleanup(self, string):
        try:
            return int(self.str_int_cleanup(string))
        except:
            return None


    def url_cleanup(self, pathname_or_href):
        origin = 'https://www.infoempleo.com/'
        href = pathname_or_href
        try:
            if not (origin in pathname_or_href):
                href = origin + pathname_or_href
        except Exception as e:
            print('Error in CleanupPipeline.url_cleanup(%s): %s'%(href,e))
        return href

    def get_text_between_parenthesis2(self, string):
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

    def get_text_between_parenthesis(self, string):
        text_list = re.findall('\(([\d\w\s-]+)\)', string)
        return text_list

    def get_text_before_parenthesis(self, string):
        text = string
        while True:
            try:
                text = re.findall('(.+)\(', text)[0].strip()
            except:
                break
        return text

    def get_a_list(self, string):
        return re.split(',| y |;|\n', string)

    def get_int_numbers(self, string):
        try:
            numbers = re.findall('(\d[0-9.,]*)', string)
            numbers = list(map(lambda e: int(e.replace('.', '')), numbers))
        except:
            numbers = []
        return numbers

    def get_text_after_key(self, key, text):
        try:
            text = re.findall('%s (.*)' % key, text.lower())[0]
        except:
            text = ''
        return text.strip()

    def get_date_as_date(self, string):
        print('#get_date_as_date: %s'%string)
        try:
            date_str = re.findall("[\d]{1,2}[/-][\d]{1,2}[/-][\d]{4}", string)[0]
            print(date_str)
            date_list = re.split('/|-|\n', date_str)
            print(date_list)
            date_list = [int(e) for e in date_list]
            date_list.reverse()
            print(date_list)
            date_date = datetime.date(*date_list)
            print(date_date)
        except:
            date_date = None
        print(date_date)
        return date_date


class CleanPipeline(CleanupPipeline_):

    def __init__(self):

        self.cleanup = {
            'Job': self._job_cleanup,
            'Company': self._company_cleanup,
        }

    def _country_cleanup(self, string):

        if 'Empleo en' in string:
            country = string.replace('Empleo en Otros Paises', "").replace('Empleo en ', "")
        else:
            l = self.get_text_between_parenthesis(string)
            if l:
                country = l[-1]
            else:
                country = ''
        return country

    def _province_cleanup(self, string):
        print('#province_cleanup')
        l = self.get_text_between_parenthesis(string)
        if l and len(l[-1]) > 3:
            province = l[-1]
        else:
            province = string
        print('#province: %s'%province)
        return province

    def _city_cleanup2(self, string):
        city = string
        if '(' in city:
            city = city[0:city.find('(')].strip()
        return city

    def __get_city_names(self, city_name):
        cities = self.get_a_list(city_name)
        cities = self.list_cleanup(cities)
        return cities
    """
    def city_cleanup(self, string):
        print('#city_cleanup:')
        try:
            city = re.findall('(.+)\(.+\)', string)[0].strip()
        except:
            city = string
        cities = self.__get_city_names(city)
        return cities
    """

    def __city_cleanup(self, string):
        city = self.get_text_before_parenthesis(string)
        parenthesis = self.get_text_between_parenthesis(string)
        if parenthesis and len(parenthesis[0]) < 4:
            city = parenthesis[0].capitalize() + " " + city
        return city

    def _cities_cleanup(self, string):
        cities = self.get_a_list(string)
        return [self.__city_cleanup(city) for city in cities]

    def _type_jobs_results_cleanup(self, url):
        return re.findall('ofertas-internacionales|primer-empleo|trabajo', url)[0]

    def _type_cleanup(self, string):
        if 'extranjero' in string:
            return "ofertas-internacionales" #Trabajo en el extranjero
        else:
            return "trabajo" #Trabajo

    def _nationality_cleanup(self, string):
        if 'extranjero' in string:
            return "internacional"
        else:
            return "nacional"

    def _company_id_cleanup2(self, url):
        try:
            href = self.url_cleanup(url)
            return href.split('/')[-2]
        except:
            return "." #%

    def _job_date_cleanup(self, string):
        today = datetime.date.today()
        try:
            number = self.int_cleanup(string)
            job_date = today
            if 'dia' in string:
                job_date = today - relativedelta(days=number)
            elif 'mes' in string:
                job_date = today - relativedelta(months=number)
            elif 'año' in string:
                job_date = today - relativedelta(years=number)
        except:
            job_date = None
        return job_date

    def __get_specify_info_from_summary_list(self, key, summary_list):
        try:
            info = list(filter(lambda e: key in e.lower(), summary_list))[0]
        except:
            info = ''
        return info

    def _get_experience(self, summary_list):
        return self.__get_specify_info_from_summary_list('experiencia', summary_list)

    def _experience_cleanup(self, experience):
        exp = self.get_int_numbers(experience) # can have length 0,1 or 2
        exp = (exp + exp + [0, 0])[0:2]
        minimum_experience = exp[0]
        recommendable_experience = exp[1]
        return minimum_experience, recommendable_experience

    def _get_salary(self, summary_list):
        try:
            salary_keys = ['salario', 'entre', 'retribución']
            salary = list(filter(lambda e: any(ele in e.lower() for ele in salary_keys), summary_list))[0]
        except:
            salary = ''
        return salary

    def _salary_cleanup(self, salary):
        money = self.get_int_numbers(salary) # can have length 0,1 or 2
        money = (money + money + [0, 0])[0:2]
        minimum_salary = money[0]
        maximum_salary = money[1]
        return minimum_salary, maximum_salary

    def _get_working_day(self, summary_list):
        return self.__get_specify_info_from_summary_list('jornada', summary_list)

    def _working_day_cleanup(self, working_day):
        return self.get_text_after_key('jornada', working_day)

    def _get_contract(self, summary_list):
        return self.__get_specify_info_from_summary_list('contrato', summary_list)

    def _contract_cleanup(self, contract):
        return self.get_text_after_key('contrato', contract)


    def _summary_cleanup(self, item):
        print('#summary_cleanup: %s'%item['summary'])
        summary = item['summary']
        summary_list = re.split('-', summary)
        summary_list = self.list_cleanup(summary_list)
        print('summary_list: %s'%summary_list)
        experience = self._get_experience(summary_list)
        print('#experience: %s' % (experience))
        item['minimum_years_of_experience'], item['recommendable_years_of_experience'] = self._experience_cleanup(experience)
        salary = self._get_salary(summary_list)
        print('#salary: %s' % (salary))
        item['minimum_salary'], item['maximum_salary'] = self._salary_cleanup(salary)
        working_day = self._get_working_day(summary_list)
        print('#working_day: %s' % (working_day))
        item['working_day'] = self._working_day_cleanup(working_day)
        contract = self._get_contract(summary_list)
        print('#contract: %s' % (contract))
        item['contract'] = self._contract_cleanup(contract)
        item['_experience'] = experience
        item['_salary'] = salary
        item['_working_day'] = working_day
        item['_contract'] = contract
        print('#set: %s %s %s %s'%(experience, salary, working_day, contract))
        print('#experience:  %s %s' % (item['minimum_years_of_experience'], item['recommendable_years_of_experience']))
        print('#salary:  %s %s' % (item['minimum_salary'], item['maximum_salary']))
        print('#summary: %s'%summary_list)
        return summary_list


    """
    def ie_item_cleanup(self, item):
        print('CleanupPipeline.job_item_cleanup')
        item['name'] = self.str_cleanup(item['name'])
        item['type'] = self.type_jobs_results_cleanup(item['type'])
        item['summary'] = self.summary_cleanup(item)
        item['id'] = self.int_cleanup(item['id'])
        item['job_date'] = self.job_date_cleanup(item['job_date'])
        item['registered_people'] = self.int_cleanup(item['registered_people'])
        item['province_name'] = self.province_cleanup(item['province_name'])
        item['city_name'] = self.cities_cleanup(item['city_name'])
        item['nationality'] = self.nationality_cleanup(item['nationality'])
        if item['nationality'] == "nacional":
            item['country_name'] = 'España'
        else:
            item['country_name'] = self.country_cleanup(item['country_name'])
        item['company_name'] = self.str_cleanup(item['company_name'])
        item['company_link'] = self.url_cleanup(item['company_link'])
        item['company_offers'] = self.int_cleanup(item['company_offers'])
        item['expiration_date'] = self.get_date_as_date(item['expiration_date'])
        return item
    """


    def _company_cleanup(self, item):
        item['company_name'] = self.str_cleanup(item['company_name'])
        item['company_link'] = self.url_cleanup(item['company_link'])
        item['company_offers'] = self.int_cleanup(item['company_offers'])
        return item

    def _job_cleanup(self, item):
        item['name'] = self.str_cleanup(item['name'])
        item['type'] = self._type_jobs_results_cleanup(item['type'])
        item['summary'] = self._summary_cleanup(item)
        item['id'] = self.int_cleanup(item['id'])
        item['job_date'] = self._job_date_cleanup(item['job_date'])
        item['registered_people'] = self.int_cleanup(item['registered_people'])
        item['province_name'] = self._province_cleanup(item['province_name'])
        item['city_name'] = self._cities_cleanup(item['city_name'])
        item['nationality'] = self._nationality_cleanup(item['nationality'])
        if item['nationality'] == "nacional":
            item['country_name'] = 'España'
        else:
            item['country_name'] = self._country_cleanup(item['country_name'])
        item['expiration_date'] = self.get_date_as_date(item['expiration_date'])
        try:
            company = item['company']
            item['company'] = self.cleanup[company.get_model_name()](company)
        except Exception as e:
            print(e)
        return item


    def process_item(self, item, spider):
        try:
            return self.cleanup[item.get_model_name()](item)
        except Exception as e:
            print('Error: {}'.format(e))
            return item
        #return self.ie_item_cleanup(item)


class StorePipeline(object):


    def __init__(self):

        self.store= {
            'Job': self._store_job,
            'Company': self._store_company,
        }

    def open_spider(self, spider):
        self.jobs = 0
        self.errors = 0

    def __set_item(self, item, dictionary):
        for k,v in dictionary.items():
            try:
                item[k] = v
            except:
                pass
        return item


    def __get_city(self, city_name, province=None, country=None):

        if not city_name:
            return None

        city = None
        if country and country.name == 'España':
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
            elif province and (not cities) and (city_name != province.name):
                city = City.objects.create(name=city_name, province=province, country=country)

        elif country and (city_name != country.name):
            city, is_a_new_city = City.objects.get_or_create(name=city_name, province=province, country=country)

        else:
            cities = City.objects.filter(name__iexact=city_name)
            if not cities:
                cities = City.objects.filter(name__icontains=city_name)
                try:
                    if not '/' in cities[0]:
                        cities =  []
                except:
                    cities = []
            if cities and len(cities) == 1:
                city = cities[0]
        return city

    def __get_location(self, cities_name, province_name, country_name):

        print('#Pipeline__get_location: %s %s %s'%(cities_name, province_name, country_name))
        country = None
        province = None
        if country_name:
            country, is_a_new_country = Country.objects.get_or_create(name=country_name)
        try:
            provinces = Province.objects.filter(name__iexact=province_name)
            print('provinces %s' % provinces)
            province = provinces[0]
        except:
            print('Error getting the province')
        print('Country: %s'%country)
        cities = []
        for city_name in cities_name:
            cities.append(self.__get_city(city_name, province, country))
        cities = list(filter(lambda c: c, cities ))
        print('#_get_location return: %s %s %s'%(cities, province, country))
        return cities, province, country


    def _store_company(self, item):
        print('*store_company')
        company_dict = item.get_dict_deepcopy()
        company_id = company_dict.pop('company_name', None)
        city = self.__get_city(company_dict['company_city_name'])
        company_dict.setdefault('created_at', timezone.now())
        company_dict.setdefault('company_city', city)
        company = None
        try:
            company, is_a_new_company_created = Company.objects.get_or_create(company_name=company_id, defaults=company_dict)
            if not is_a_new_company_created:
                company.company_offers = company_dict['company_offers']
                company.updated_at = timezone.now()
                company.save()
        except Exception as e:
            print('Company.objects.get_or_create')
            print(e)

        return company


    def _store_job(self, item):
        try:
            company = item['company']
            item['company'] = self.store[company.get_model_name()](company)
        except Exception as e:
            print(e)
        job_dict = copy.deepcopy(item.get_dict_deepcopy())
        job_id = job_dict.pop('id', None)
        job_dict.setdefault('created_at', timezone.now())
        job, is_new_item_created = Job.objects.get_or_create(id=job_id, defaults=job_dict)
        if not is_new_item_created:
            if job_dict['type'] == 'primer-empleo' or not job.type:
                job.type = job_dict['type']
            job.expiration_date = job_dict['expiration_date']
            job.vacancies_update = job_dict['vacancies']
            job.updated_at = timezone.now()
        else:
            cities, province, country = self.__get_location(item['city_name'], item['province_name'], item['country_name'])
            job.country = country
            job.province = province
            for city in cities:
                job.cities.add(city)
        job.save()
        print('#store_job: %s'%job)
        return job



    def process_item(self, item, spider):
        try:
            return self.store[item.get_model_name()](item)
        except:
            return item
        """
        print()
        print('StorePipeline.process_item')

        try:
            company_item = self.store_company(item)
        except Exception as e:
            print('Error storing the company in pipeline: %s'%e)
            print('item: %s'%item)
            print('Successful: %i, Errors: %i'%(self.jobs, self.errors))
            company_item = None
        try:
            self.store_job(item, company_item)
            self.jobs += 1
        except Exception as e:
            print('Error storing the job in pipeline: %s' % e)
            self.errors += 1
            #print('item: %s' % item)
            print('Successful: %i, Errors: %i' % (self.jobs, self.errors))
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print()
        print('Successful: %i, Errors: %i' % (self.jobs, self.errors))
        print()
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        return item
        """

class SqlitePipeline(object):

    db = "ie2.db"
    def __init__(self):
        self.create_connection()
        self.drop_tables() #%
        self.create_tables()


    def create_connection(self):
        self.connection = sqlite3.connect(self.db)
        self.curr = self.connection.cursor()


    def create_tables(self):
        self.create_jobs_table()
        self.create_companies_table()

    def drop_tables(self):
        self.curr.execute("""drop table if exists jobs""")
        self.connection.commit()
        self.curr.execute("""drop table if exists companies""")
        self.connection.commit()


    def create_jobs_table(self):
        self.curr.execute("""create table IF NOT EXISTS jobs( 
        id integer,
        name text,
        link text,
        company_id text,
        area text,
        requisites text, 
        city text,
        country text,
        nationality text,
        subscribers integer,
        time text
        )""")
        self.connection.commit()

    def create_companies_table(self):
        self.curr.execute("""create table IF NOT EXISTS companies( 
                id integer,
                name text,
                link text,
                city text,
                category text,
                description text, 
                vacancies integer
               )""")
        self.connection.commit()

    def store_item(self, item):
        item_name = item.get_name()
        if item_name == 'JobItem':
            self.insert_job(item.tuple_of_values())
        elif item_name == 'CompanyItem':
            self.insert_company(item.tuple_of_values())

    def insert_job(self, tuple):
        print('INSERT JOB')
        print(tuple)
        print([type(e) for e in tuple])
        self.curr.execute("""insert into jobs values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple)
        self.connection.commit()

    def insert_company(self, tuple):
        self.curr.execute("""insert into jobs values(?, ?, ?, ?, ?, ? ,?)""", tuple)
        self.connection.commit()

    def process_item(self, item, spider):
        self.store_item(item)
        return item

    def close_spider(self, spider):
        self.curr.close()
        self.connection.close()


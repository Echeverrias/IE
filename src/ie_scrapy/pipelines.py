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
from job.models import Job, Company, Country, City, Province, Language
from language_utilities import get_languages_and_levels_pairs
from utilities import (
    get_int_list,
    get_text_before_sub,
    replace_multiple,
    save_error,
)
from .items import JobItem, CompanyItem
from django.db import transaction

STATE_CREATED = Job.STATE_CREATED
STATE_UPDATED = Job.STATE_UPDATED
STATE_CLOSED = Job.STATE_CLOSED

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
        origin = 'https://www.infoempleo.com'
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
        l = re.split(', |; |,|;| y | and | o | or |\n', string)
        l = [i.strip() for i in l]
        return l

    """
    def get_int_list2(self, string):
        try:
            numbers = re.findall('(\d[0-9.,]*)', string)
            numbers = list(map(lambda e: int(e.replace('.', '')), numbers))
        except:
            numbers = []
        return numbers
    """

    def find_apparitions(self, string, char):
        return [i for i, c in enumerate(string) if c == char]

    def get_int_list(self, string):
        try:
            numbers = re.findall('(\d[0-9.,]*)', string)
            numbers_ = []
            for number in numbers:
                ii = self.find_apparitions(number, '.')
                if ii:
                    last_i = ii[len(ii) - 1]
                if ii and (last_i + 3) >= len(number):
                    number = number[0:last_i] + ',' + number[last_i + 1:len(number)]
                numbers_.append(number)
            numbers_ = list(map(lambda e: round(float(e.replace('.', '').replace(',', '.'))), numbers_))
        except Exception as e:
            numbers_ = []
        return numbers_

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


    def _get_end_index(self, text, start=0):
        return min(len(text) - 1, text.find('\n', start))


    def _get_slice_from_sub_to_end(self, isub, text):
        start = text.lower().find(isub)
        if start < 0:
            return ""
        else:
            start = start + len(isub)
        end = self._get_end_index(text, start)
        return text[start:end+1].strip()

    @classmethod
    def get_acronym(cls, string):
        acronym = ''.join(re.findall(r'[A-ZÁÉÍÓÚ]', string))
        acronym = acronym.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        print();print(f'Acronym of {string}: {acronym}');print()
        return acronym



class CleanPipeline(CleanupPipeline_):

    def __init__(self):

        self.cleanup = {
            'Job': self._job_cleanup,
            'Company': self._company_cleanup,
        }

    def _country_cleanup(self, string):

        if 'Empleo en' in string:
            empleo = re.compile(r'(E|e)mpleo en (O|o)tros (P|p)a(i|í)ses|(E|e)mpleo en ')
            country = empleo.sub("", string)
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


    def __city_cleanup(self, string):
        city = self.get_text_before_parenthesis(string)
        parenthesis = self.get_text_between_parenthesis(string)
        if parenthesis and len(parenthesis[0]) < 4:
            # Bercial (el) -> el Bercial
            city = parenthesis[0].capitalize() + " " + city
        if city.isupper():
            city = city.title()
        alrededores = re.compile(r'(a|A)ldedores|(a|A)lredores|(a|A)lredor|(a|A)lrededores')
        city = alrededores.sub("Alrededores", city)
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

    def _state_cleanup(self, string):
        return replace_multiple(string, ['¡','!','\(', '\)'], "")

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
        print(f'CleanPipeline._job_date_cleanup({string})')
        today = datetime.date.today()
        try:
            number = self.int_cleanup(string)
            print(f'number{number}')
            job_date = today
            if 'dia' in string or 'día' in string or 'hora' in string:
                if 'hora' in string:
                    number = int(number/24)
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
        exp = self.get_int_list(experience) # can have length 0,1 or 2
        exp = (exp + exp + [0, 0])[0:2]
        minimum_experience = exp[0]
        recommendable_experience = exp[1]
        return minimum_experience, recommendable_experience

    def _get_salary(self, summary_list):
        try:
            salary_keys = ['salario', 'retribución', 'bruto', '€']
            salary = list(filter(lambda e: any(ele in e.lower() for ele in salary_keys), summary_list))[0]
        except:
            salary = ''
        return salary

    def _salary_cleanup(self, salary):
        money = self.get_int_list(salary) # can have length 0,1 or 2
        money = (money + money + [None, None])[0:2]
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

    def _get_annual_salary(self, text):
        KEYS = {
            'year': ['bruto anual', 'b/a', 'bruto al año'],
            'month': ['bruto mensual', 'b/m', 'bruto al mes'],
            'day': ['bruto al día', 'b/d', 'bruto al día'],
        }
        salary = [None, None]
        if text:
            salary_type_tl = [(sub, text.find(sub)) for sub in KEYS['year'] if text.find(sub) > 0]
            if salary_type_tl:
                is_monthly_salary = False
            else:
                salary_type_tl = [(sub, text.find(sub)) for sub in KEYS['month'] if text.find(sub) > 0]
                is_monthly_salary = True
            if salary_type_tl:
                i_salary = max(0, text.lower().find('salar'))
                if i_salary == 0:
                    text_ = get_text_before_sub(text, salary_type_tl[0][0], distance=25, separators=['\n', '\r'])
                else:
                    text_ = text[i_salary:salary_type_tl[0][1]]
                salary = self._salary_cleanup(text_)
                if salary and is_monthly_salary:
                    salary = [i * 12 for i in salary]
        return salary


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
        if not item['minimum_salary']:
            print('Looking for salary in "it_is_offered"')
            item['minimum_salary'], item['maximum_salary'] = self._get_annual_salary(item['it_is_offered'])
        working_day = self._get_working_day(summary_list)
        print('#working_day: %s' % (working_day))
        item['working_day'] = self._get_working_day(summary_list)# self._working_day_cleanup(working_day)
        contract = self._get_contract(summary_list)
        print('#contract: %s' % (contract))
        item['contract'] = self._get_contract(summary_list)# self._contract_cleanup(contract)
        item['_experience'] = experience
        item['_salary'] = salary
        item['_working_day'] = working_day
        item['_contract'] = contract
        print('#set: %s %s %s %s'%(experience, salary, working_day, contract))
        print('#experience:  %s %s' % (item['minimum_years_of_experience'], item['recommendable_years_of_experience']))
        print('#salary:  %s %s' % (item['minimum_salary'], item['maximum_salary']))
        print('#summary: %s'%summary_list)
        return summary_list

    def _job_dates_cleanup(self, item):
        print('CleanUpPipeline._job_dates_cleanup')
        if item['state'] == STATE_CREATED:
            item['first_publication_date'] = self._job_date_cleanup(item['first_publication_date'])
            item['last_update_date'] = None
        elif item['state'] == STATE_UPDATED:
            item['last_update_date'] = self._job_date_cleanup(item['last_update_date'])
            item['first_publication_date'] = None
        return item


    def _company_cleanup(self, item):
        item['company_name'] = self.str_cleanup(item['company_name'])
        item['company_link'] = self.url_cleanup(item['company_link'])
        item['company_offers'] = self.int_cleanup(item['company_offers'])
        return item

    def _job_cleanup(self, item):
        print('CleanPipeline._job_cleanup')
        item['name'] = self.str_cleanup(item['name'])
        item['state']= self._state_cleanup(item['state'])
        item['type'] = self._type_jobs_results_cleanup(item['type'])
        item['summary'] = self._summary_cleanup(item)
        item['id'] = self.int_cleanup(item['id'])
        item['registered_people'] = self.int_cleanup(item['registered_people'])
        item['provincename'] = self._province_cleanup(item['provincename'])
        item['cityname'] = self._cities_cleanup(item['cityname'])
        item['nationality'] = self._nationality_cleanup(item['nationality'])
        item = self._job_dates_cleanup(item)
        if item['nationality'] == "nacional":
            item['countryname'] = 'España'
        else:
            item['countryname'] = self._country_cleanup(item['countryname'])
        item['expiration_date'] = self.get_date_as_date(item['expiration_date'])
        try:
            company = item['company']
            item['company'] = self.cleanup[company.get_model_name()](company)
        except Exception as e:
            print(e)
        return item


    def process_item(self, item, spider):
        print('CleanPipeline.process_item')
        try:
            clean_item = self.cleanup[item.get_model_name()](item)
            print('ITEM CLEANED:')
            print(clean_item)
            return clean_item
        except Exception as e:
            print('Error CleanPipeline.process_item: {}'.format(e))
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

    def _get_languages(self, string):
        print('_get_languages')
        print()
        print('GET_LANGUAGES')
        language_and_level_pairs = get_languages_and_levels_pairs(string)
        print(f'language_and_level_pairs: {language_and_level_pairs}')
        languages = []
        for l_l in language_and_level_pairs:
            print(f'l_l: {l_l}')
            language, is_new_language = Language.objects.get_or_create(name=l_l[0], level=l_l[1])
            print(f'language: {language}')
            languages.append(language)
        print(f'languages: {languages}')
        return languages

    def __get_city(self, city_name, province=None, country=None):
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print(f'__get_city{city_name, province, country}')
        if not city_name:
            return None

        city = None
        if country and country.name == 'España':
            print('The country is España')
            # first search with iexact
            if province:
                print('Province <> None (iexact)')
                cities_qs = City.objects.filter(country=country, province=province, name__iexact=city_name)
            else:
                print('Province == None (iexact)')
                cities_qs = City.objects.filter(country=country, name__iexact=city_name)
            print(f'result: {cities_qs}')
            # second search with icontains
            if cities_qs:
                city = cities_qs[0]
            else:
                print('not iexact city found')
                if province:
                    print('Province <> None (icontains)')
                    cities_qs = City.objects.filter(country=country, province=province, name__icontains=city_name)
                else:
                    print('Province == None (icontains)')
                    cities_qs = City.objects.filter(country=country, name__icontains=city_name)
                print(f'result: {cities_qs}')
                if cities_qs.count() > 1:
                    print(f'more than one result')
                    cities_qs = cities_qs.filter(name__icontains='/')
                    for city in cities_qs:
                        cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                    cities_qs = cities
                if cities_qs:
                    city = cities_qs[0]
                    if province:
                        city.province = province
                        city.save()
                elif province and (city_name != province.name):
                    city = City.objects.create(name=city_name, province=province, country=country)

        elif country and (city_name.lower() == country.name.lower() or city_name.lower() == CleanupPipeline_.get_acronym(country.name).lower()):
            return None
        # a foreign city:
        elif country :
            cities_qs = City.objects.filter(name__iexact=city_name,  country=country)
            if cities_qs:
                city = cities_qs[0]
            else:
                city, is_a_new_city = City.objects.get_or_create(name=city_name, country=country)
        else:
            cities_qs = City.objects.filter(name__iexact=city_name)
            if not cities_qs:
                cities_qs = City.objects.filter(name__icontains=city_name)
                if cities_qs and cities_qs.count() > 1:
                    cities_qs = cities_qs.filter(name__icontains='/')
                    for city in cities_qs:
                        cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                    cities_qs = cities
                if cities_qs:
                    city = cities_qs[0]
        return city

    def __get_location(self, city_names, province_name, country_name):

        print('#Pipeline__get_location: %s %s %s'%(city_names, province_name, country_name))
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
        for city_name in city_names:
            cities.append(self.__get_city(city_name, province, country))
        # Deleting the null cities:
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

    def _set_location(self, job, item):
        print('StorePipeline._set_location')
        cities, province, country = self.__get_location(item['cityname'], item['provincename'], item['countryname'])
        print(cities, province, country)

        #job.country = country
        #job.province = province
        job.cities.clear()
        job.cities.set(cities)
        print(job);print();print()

        return job

    def _set_languages(self, job, item):
        print('StorePipeline._set_languages')
        languages = self._get_languages(item['requirements'])
        print(f'languages: {languages}')
        job.languages.clear()
        job.languages.set(languages)
        print(job);print();print()
        return job

    # Checks for any change in the offer
    def _has_been_updated(self, job, item):
        update = (
            (item['state'] == STATE_UPDATED) and (item['last_update_date'] != job.last_update_date) or
            (item['state'] == STATE_CREATED) and (item['firs_publication_date'] != job.first_publication_date) or
            (item['state'] == STATE_CLOSED) and (item['expiration_date'] != job.expiration_date)
        )
        if (not update) and (item['state'] == STATE_CLOSED) and (job.state != STATE_CLOSED):
            update = (
                job['vacancies'] != item['vacancies'] or
                job['type'] != item['type'] or
                job['contract'] != item['contract'] or
                job['working_day'] != item['working_day'] or
                job['minimum_years_of_experience'] != item['minimum_years_of_experience'] or
                job['recommendable_years_of_experience'] != item['recommendable_years_of_experience'] or
                job['minimum_salary'] != item['minimum_salary'] or
                job['maximum_salary'] != item['maximum_salary'] or
                job['functions'] != item['functions'] or
                job['requirements'] != item['requirements'] or
                job['it_is_offered'] != item['it_is_offered'] or
                job['area'] != item['area'] or
                job['category_level'] != item['category_level']
            )
        print(f'UPDATE: {update}')
        return update


    def _update_job(self, job, item):
        # if job.last_update_date != item['last_update_date']: -> Actualizamos cuando la oferta ha caducado (por si no hemos hecho scraping  sobre una actualización)

        if self._has_been_updated(job, item):
            print('1')
            job_dict = copy.deepcopy(item.get_dict_deepcopy())
            job_dict.pop('id', None)
            if item['state'] != STATE_CREATED:
                job_dict.pop('first_publication_date', None)
                if item['state'] == STATE_CLOSED and not item['expiration_date']:
                    job_dict.pop('expiration_date', None)
            id = job.id
            qs = Job.objects.filter(id=id)
            qs.update(**job_dict)
            self._set_location(job, item)
            self._set_languages(job, item)
        elif job.registered_people != item['registered_people']:
            print('2')
            job.registered_people = item['registered_people']
            job.state = item['state'] #ñapa
            job.save()
        elif job.state != item['state']:
            print('3')
            job.state = item['state']
            job.save()


    def _store_job(self, item):
        print('*store_job')
        try:
            company = item['company']
            print(company)
            item['company'] = self.store[company.get_model_name()](company)
        except Exception as e:
            print(f'Error StorePipeline._store_job (storing company){e}')
        job_dict = copy.deepcopy(item.get_dict_deepcopy())
        job_id = job_dict.pop('id', None)
        job, is_new_item_created = Job.objects.get_or_create(id=job_id, defaults=job_dict)
        print('??????????????????????????????????????????????????')
        print(f'id: {job.id}')
        print(job.get_absolute_url())
        print(job)
        print(f'is_new_item_created: {is_new_item_created}')
        if not is_new_item_created:
            ##ñapa ########################
            self._set_location(job, item)
            self._set_languages(job, item)
            ###############################
            self._update_job(job, item)
        else:
            print('NEW JOB CREATED')
            self._set_location(job, item)
            self._set_languages(job, item)
        print('#store_job: %s'%job)
        return job


    def process_item(self, item, spider):
        print('StorePipeline.process_item')
        print(item)
        try:
            return self.store[item.get_model_name()](item)
        except Exception as e:
            print(f'Error StorePipeline.process_item: {e}')
            save_error({'error': e, 'description':'Error StorePipeline.process_item','id':item['id'], 'link':item['link']})
            return item
        """
        print()
        print('StorePipeline.process_item')

        try:
            company_item = self.store_company(item)
        except Exception as e:
            print('Error storing the company in pipeline: %s'%e)
            print('item: %s'%item)
            print('Successful: %i, Errors: %i'%(self.job, self.errors))
            company_item = None
        try:
            self.store_job(item, company_item)
            self.job += 1
        except Exception as e:
            print('Error storing the job in pipeline: %s' % e)
            self.errors += 1
            #print('item: %s' % item)
            print('Successful: %i, Errors: %i' % (self.job, self.errors))
        print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        print()
        print('Successful: %i, Errors: %i' % (self.job, self.errors))
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
        self.curr.execute("""drop table if exists job""")
        self.connection.commit()
        self.curr.execute("""drop table if exists companies""")
        self.connection.commit()


    def create_jobs_table(self):
        self.curr.execute("""create table IF NOT EXISTS job( 
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
        self.curr.execute("""insert into job values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tuple)
        self.connection.commit()

    def insert_company(self, tuple):
        self.curr.execute("""insert into job values(?, ?, ?, ?, ?, ? ,?)""", tuple)
        self.connection.commit()

    def process_item(self, item, spider):
        self.store_item(item)
        return item

    def close_spider(self, spider):
        self.curr.close()
        self.connection.close()


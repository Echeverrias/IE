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
    get_int_list_from_string,
    get_text_before_sub,
    replace_multiple,
    save_error,
    raise_function_exception,
    get_coincidences,
    get_acronym,
    get_string_number_from_string,
    get_int_from_string,
    find_indexes_apparitions,
    get_text_between_parenthesis,
    get_text_before_parenthesis,
    get_int_list_from_string,
    get_text_after_key,
    get_date_from_string,
    get_end_index_of_a_paragraph_from_string,
    get_slice_from_sub_to_end_of_the_paragraph,
    get_a_list_of_enumerates_from_string,
    trace,

)

import time
from .items import JobItem, CompanyItem
from django.db import transaction


debug={'location':None, 'value':None, 'value_in': None, 'value_out':None}


class CleanupPipeline_(object):

    def clean_string(self, string):
        print('#clean_string: %s'%string)
        try:
            clean_string = string.strip()
        except Exception as e:
            clean_string = ''
        return clean_string

    def clean_string_list(self, some_list):
        return list(map(lambda e: e.strip(), some_list))


class CleanPipeline(CleanupPipeline_):

    def __init__(self):

        self._cleanup = {
            'Job': self._clean_job,
            'Company': self._clean_company,
        }

        self.job_areas = [ t[0] for t in Job.AREA_CHOICES]


    def _clean_url(self, pathname_or_href):
        origin = 'https://www.infoempleo.com'
        href = pathname_or_href
        try:
            if not (origin in pathname_or_href):
                href = origin + pathname_or_href
        except Exception as e:
            print('Error in CleanupPipeline._clean_url(%s): %s'%(href,e))
        return href

    def _clean_country(self, string):
        try:
            if 'Empleo en' in string:
                empleo = re.compile(r'(E|e)mpleo en (O|o)tros (P|p)a(i|í)ses|(E|e)mpleo en ')
                country = empleo.sub("", string)
            else:
                l = get_text_between_parenthesis(string)
                if l:
                    country = l[-1]
                else:
                    country = ''
            return country
        except TypeError as e:
            return ''

    def _clean_province(self, string):
        try:
            print(f'#province_cleanup({string})')
            l = get_text_between_parenthesis(string)
            print(f'value_out-get_text_between_parenthesis: {l}')
            if l and len(l[-1]) > 3:
                province = l[-1]
            else:
                province = string or ''
            print(f'value_out-_province_clenaup: {province}');
            return province
        except TypeError as e:
            print(f'_clean_province -> Error: {e}')
            return ''

    def _city_cleanup2(self, string):
        city = string
        if '(' in city:
            city = city[0:city.find('(')].strip()
        return city


    def _clean_city(self, string):
        try:
            debug['_city_cleanup - init'] = f'arg: {string}'
            print(f'$$_clean_city({string})')
            debug['_citiy_cleanup'] = f'get_text_before_parenthesis({string})'
            city = get_text_before_parenthesis(string) or string
            debug['_citiy_cleanup - city'] = f'{city}'
            debug['_citiy_cleanup'] = f'get_text_between_parenthesis({string})'
            parenthesis = get_text_between_parenthesis(string)
            debug['_citiy_cleanup - parenthesis'] = f'{parenthesis}'
            if parenthesis and len(parenthesis[0]) < 4:
                # Bercial (el) -> el Bercial
                city = parenthesis[0].capitalize() + " " + city
            debug['_citiy_cleanup - city2'] = f'{city}'
            if city and city.isupper():
                city = city.title()
            debug['_citiy_cleanup - city3'] = f'{city}'
            alrededores = re.compile(r'(a|A)ldedores|(a|A)lredores|(a|A)lredor|(a|A)lrededores')
            debug['_city_cleanup'] = f'sub({"Alrededores", city})'
            city = alrededores.sub("Alrededores", city)
            debug['_citiy_cleanup - city4'] = f'{city}'
            print(city)
            debug['_city_cleanup'] = f'replace({city})'
            city = city.replace('.', "")
            debug['_citiy_cleanup - city5'] = f'{city}'
            print(city)
            debug['_city_cleanup - return'] = f'return: {city}'
            return city.strip()
        except Exception as e:
            debug['_citiy_cleanup - error'] = f'error: {e}'
            return ''

    def _clean_cities(self, string):
        cities = get_a_list_of_enumerates_from_string(string)
        debug['_clean_cities'] = f'{len(cities)} cities: {cities}'
        return [self._clean_city(city) for city in cities]

    def _clean_job_type(self, url):
        return re.findall('ofertas-internacionales|primer-empleo|trabajo', url)[0]


    def _clean_state(self, string):
        print(f'_state_clean_up{string}')
        if string:
            states = [Job.STATE_CREATED, Job.STATE_UPDATED, Job.STATE_CLOSED]
            states_coincidences = get_coincidences(string, states)
            if states_coincidences:
                return states_coincidences[0]
        return Job.STATE_WITHOUT_CHANGES

    def _clean_nationality(self, string):
        """
        Comprueba la url de la oferta:
        - Si es una oferta inernacional devuelve 'internacional'
        - Si es no una oferta inernacional devuelve 'nacional'
        :param string:
        :return: "international" or "nacional"
        """
        if 'extranjero' in string:
            return "internacional"
        else:
            return "nacional"


    def _company_id_cleanup2(self, url):
        # DEPRECATED
        try:
            href = self._clean_url(url)
            return href.split('/')[-2]
        except:
            return "." #%

    def _clean_job_date(self, string):
        print(f'CleanPipeline._clean_job_date({string})')
        today = datetime.date.today()
        try:
            number = get_int_from_string(string)
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
        except Exception as e:
            job_date = None
        return job_date

    def _get_specify_info_from_summary_list(self, key, summary_list):
        try:
            info = list(filter(lambda e: key in e.lower(), summary_list))[0]
        except:
            info = ''
        return info

    def _get_experience(self, summary_list):
        return self._get_specify_info_from_summary_list('experiencia', summary_list)

    def _clean_experience(self, experience):
        exp = get_int_list_from_string(experience) # can have length 0,1 or 2
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

    def _clean_salary(self, salary):
        money = get_int_list_from_string(salary) # can have length 0,1 or 2
        money = (money + money + [None, None])[0:2]
        minimum_salary = money[0]
        maximum_salary = money[1]
        return minimum_salary, maximum_salary

    def _get_working_day(self, summary_list):
        return self._get_specify_info_from_summary_list('jornada', summary_list)

    def _clean_working_day(self, working_day):
        return get_text_after_key('jornada', working_day)

    def _get_contract(self, summary_list):
        return self._get_specify_info_from_summary_list('contrato', summary_list)

    def _clean_contract(self, contract):
        return get_text_after_key('contrato', contract)

    def _clean_area(self, area):
        print(f'*!!clean_area{area} ')
        if 'Area' in area:
            area = area.replace('Area de', "").replace('Área de', "").strip()
        return area

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
                salary = self._clean_salary(text_)
                if salary and is_monthly_salary:
                    salary = [i * 12 for i in salary]
        return salary


    def _clean_summary(self, item):
        print('#summary_cleanup: %s'%item['summary'])
        summary = item['summary']
        summary_list = re.split('-', summary)
        summary_list = self.clean_string_list(summary_list)
        print('summary_list: %s'%summary_list)
        experience = self._get_experience(summary_list)
        print('#experience: %s' % (experience))
        item['minimum_years_of_experience'], item['recommendable_years_of_experience'] = self._clean_experience(experience)
        salary = self._get_salary(summary_list)
        print('#salary: %s' % (salary))
        item['minimum_salary'], item['maximum_salary'] = self._clean_salary(salary)
        if not item['minimum_salary']:
            print('Looking for salary in "it_is_offered"')
            item['minimum_salary'], item['maximum_salary'] = self._get_annual_salary(item['it_is_offered'])
        working_day = self._get_working_day(summary_list)
        print('#working_day: %s' % (working_day))
        item['working_day'] = self._get_working_day(summary_list)# self._clean_working_day(working_day)
        contract = self._get_contract(summary_list)
        print('#contract: %s' % (contract))
        item['contract'] = self._get_contract(summary_list)# self._clean_contract(contract)
        item['_experience'] = experience
        item['_salary'] = salary
        item['_working_day'] = working_day
        item['_contract'] = contract
        print('#set: %s %s %s %s'%(experience, salary, working_day, contract))
        print('#experience:  %s %s' % (item['minimum_years_of_experience'], item['recommendable_years_of_experience']))
        print('#salary:  %s %s' % (item['minimum_salary'], item['maximum_salary']))
        print('#summary: %s'%summary_list)
        return summary_list

    def _clean_job_dates(self, item):
        print('CleanUpPipeline._clean_job_dates')
        if item['state'] in [Job.STATE_CREATED, Job.STATE_WITHOUT_CHANGES]:
            item['first_publication_date'] = self._clean_job_date(item['first_publication_date'])
            item['last_update_date'] = None
        elif item['state'] ==  Job.STATE_UPDATED:
            item['last_update_date'] = self._clean_job_date(item['last_update_date'])
            item['first_publication_date'] = None
        elif item['state'] ==  Job.STATE_CLOSED:
            item['last_update_date'] = None
            item['first_publication_date'] = None
        return item


    def _clean_company(self, item):
        item['company_name'] = self.clean_string(item['company_name'])
        item['company_link'] = self._clean_url(item['company_link'])
        item['company_offers'] = get_int_from_string(item['company_offers'])
        item['company_city_name'] = self._clean_city(item['company_city_name'])
        return item

    def _clean_job(self, item):
        print('CleanPipeline._clean_job')
        item['name'] = self.clean_string(item['name'])
        item['state']= self._clean_state(item['state'])
        item['type'] = self._clean_job_type(item['type'])
        item['summary'] = self._clean_summary(item)
        item['area'] = self._clean_area(item['area'])
        item['id'] = get_int_from_string(item['id'])
        item['vacancies'] = get_int_from_string(item['vacancies'])
        item['registered_people'] = get_int_from_string(item['registered_people'])
        item['provincename'] = self._clean_province(item['provincename'])
        print(f'_job.cleanup - item["provincename"] -> {item["provincename"]}')
        item['cityname'] = self._clean_cities(item['cityname'])
        item = self._clean_job_dates(item)
        item['nationality'] = self._clean_nationality(item['nationality'])
        if item['nationality'] == "nacional":
            item['countryname'] = 'España'
        else:
            item['countryname'] = self._clean_country(item['countryname'])
        item['expiration_date'] = get_date_from_string(item['expiration_date'])
        try:
            company = item['company']
            item['company'] = self._cleanup[company.get_model_name()](company);print(13);
        except Exception as e:
            print(e)
            save_error(e, {**debug, 'pipeline': 'CleanPipeline', 'id': item['id'], 'link': item['link'], 'item': item})
        return item


    def process_item(self, item, spider):
        print('CleanPipeline.process_item')
        debug = {}
        try:
            debug.setdefault('raw item',item)
            clean_item = self._cleanup[item.get_model_name()](item)
            print('ITEM CLEANED:')
            print(clean_item)
            return clean_item
        except Exception as e:
            print('Error CleanPipeline.process_item: {}'.format(e))
            save_error(e, {**debug, 'pipeline':'CleanPipeline', 'id':item['id'], 'link':item['link'], 'item':item })
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

    def _set_item(self, item, dictionary):
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

    def _get_city(self, city_name, province=None, country=None):
        debug['location'] = f'CleanPipeline._get_city'
        debug['value'] = f'city_name {city_name}'
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
                cities_qs = City.objects.filter(name__contains=city_name) # contains to avoid coincidence in the middle of the string
                if cities_qs and cities_qs.count() > 1:
                    cities_qs = cities_qs.filter(name__icontains='/')
                    cities = None
                    for city in cities_qs:
                        cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                    cities_qs = cities
                if cities_qs:
                    city = cities_qs[0]
        return city

    def _get_location(self, city_names, province_name, country_name):
        debug['_get_location'] = f'city: {city_names}, province: {province_name}, country: {country_name})'
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
            cities.append(self._get_city(city_name, province, country))
        # Deleting the null cities:
        cities = list(filter(lambda c: c, cities ))
        print('#_get_location return: %s %s %s'%(cities, province, country))
        return cities, province, country


    def _store_company(self, item):
        print('$$store_company')
        debug['location'] = f'CleanPipeline._store_company'
        debug['company'] = item
        company_dict = item.get_dict_deepcopy()
        company_id = company_dict.pop('company_name', None)
        city = self._get_city(company_dict['company_city_name'])
        company_dict.setdefault('created_at', timezone.now())
        company_dict.setdefault('company_city', city)
        company = None
        print('$$1')
        try:
            company, is_a_new_company_created = Company.objects.get_or_create(company_name=company_id, defaults=company_dict)
            if not is_a_new_company_created:
                if company.company_offers != company_dict['company_offers']:
                    company.company_offers = company_dict['company_offers']
                    company.updated_at = timezone.now()
                    company.save()
        except Exception as e:
            print('!!Company.objects.get_or_create')
            save_error(e, {**debug, 'pipeline':'StorePipeline','company_id': item['company_name'], 'company_link': item['company_link']})
            print(e)

        return company

    def _set_location(self, job, item):
        print('StorePipeline._set_location')
        cities, province, country = self._get_location(item['cityname'], item['provincename'], item['countryname'])
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
            (item['state'] == Job.STATE_UPDATED) and (item['last_update_date'] != job.last_update_date) or
            (item['state'] in [Job.STATE_CREATED, Job.STATE_WITHOUT_CHANGES]) and (item['first_publication_date'] != job.first_publication_date) or
            (item['state'] == Job.STATE_CLOSED) and (item['expiration_date'] != job.expiration_date)
        )
        if (not update) and (item['state'] == Job.STATE_CLOSED) and (job.state != Job.STATE_CLOSED):
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
        debug['_has_been_updated']=update
        return update


    def _update_job(self, job, item):
        # if job.last_update_date != item['last_update_date']: -> Actualizamos cuando la oferta ha caducado (por si no hemos hecho scraping  sobre una actualización)
        debug['_update_job'] = f'job.id: {job.id}, item.id: {item["id"]}'
        if self._has_been_updated(job, item):
            print('1'); debug['_update_job']='_has_been_updated'
            job_dict = copy.deepcopy(item.get_dict_deepcopy())
            job_dict.pop('id', None)
            if item['state'] == Job.STATE_CLOSED:
                job_dict.pop('first_publication_date', None)
                job_dict.pop('last_update_date', None)
            elif item['state'] == Job.STATE_UPDATED:
                job_dict.pop('first_publication_date', None)
            id = job.id
            qs = Job.objects.filter(id=id)
            qs.update(**job_dict)
            self._set_location(job, item)
            self._set_languages(job, item)
        elif job.registered_people != item['registered_people']:
            debug['_update_job'] = "job.registered_people != item['registered_people']"
            job.registered_people = item['registered_people']
            job.state = item['state'] #ñapa
            job.save()
        elif job.state != item['state']:
            debug['_update_job'] = "job.state != item['state']"
            print('3')
            job.state = item['state']
            job.save()


    def _store_job(self, item):
        print('*store_job')
        try:
            debug['location'] = f'CleanPipeline._store_job'
            company = item['company']
            print(company)
            item['company'] = self.store[company.get_model_name()](company)
            debug['location'] = f'CleanPipeline._store_job (company has been stored)'
            print('$$Company stored!!')
        except Exception as e:
            print(f'!!Error StorePipeline._store_job (storing company): {e}')
            save_error(e, {**debug, 'pipeline':'StorePipeline', 'company_id': item['company_name'], 'company_link': item['company_link'], 'item': item})

        job_dict = copy.deepcopy(item.get_dict_deepcopy())
        job_id = job_dict.pop('id', None)
        debug['location'] = f'CleanPipeline._store_job get_or_create'
        job, is_new_item_created = Job.objects.get_or_create(id=job_id, defaults=job_dict)
        print('??????????????????????????????????????????????????')
        print(f'id: {job.id}')
        print(job.get_absolute_url())
        print(job)
        print(f'is_new_item_created: {is_new_item_created}')
        if not is_new_item_created:
            debug['location'] = f'CleanPipeline._store_job get_or_create not is_new_item_created'
            ##ñapa ########################
            self._set_location(job, item)
            self._set_languages(job, item)
            ###############################
            self._update_job(job, item)
        else:
            debug['location'] = f'CleanPipeline._store_job get_or_create is_new_item_created'
            print('NEW JOB CREATED')
            self._set_location(job, item)
            self._set_languages(job, item)
        print('#store_job: %s'%job)
        return job


    def process_item(self, item, spider):
        print('StorePipeline.process_item')
        print(item)
        debug = {}
        try:
            debug['cleaned item']=item
            return self.store[item.get_model_name()](item)
        except Exception as e:
            print(f'Error StorePipeline.process_item: {e}')
            save_error(e, {**debug, 'pipeline':'StorePipeline', 'model':item.get_model_name() , 'line':723, 'id':item['id'], 'link':item['link'], 'item': item})
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


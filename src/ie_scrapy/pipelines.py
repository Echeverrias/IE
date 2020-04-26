# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import functools
import re
import sqlite3
import time
import datetime
from django.utils import timezone
from django.utils.text import slugify
from django.db.utils import InterfaceError
from django import db
from django.db.models.functions import Length
import copy
from dateutil.relativedelta import relativedelta
from job.models import Job, Company, Country, City, Province, Language
from utilities.languages_utilities import get_languages_and_levels_pairs
from utilities.utilities import (
    get_int_list_from_string,
    get_text_before_sub,
    get_text_after_key,
    replace_multiple,

    get_coincidences,
    get_acronym,
    get_string_number_from_string,
    get_int_from_string,
    find_indexes_apparitions,
    get_text_between_parenthesis,
    get_text_before_parenthesis,
    get_int_list_from_string,

    get_date_from_string,
    get_end_index_of_a_paragraph_from_string,
    get_slice_from_sub_to_end_of_the_paragraph,
    get_a_list_of_enumerates_from_string,
    raise_function_exception,
    trace,
    write_in_a_file,
    save_error,

)

debug={'location':None, 'value':None, 'value_in': None, 'value_out':None}


def check_spider_pipeline(process_item_method):

    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):
        pipeline_name = self.__class__.__name__

        if self.__class__ in spider.pipelines:
            spider.logger.info(f'{pipeline_name} executing')
            return process_item_method(self, item, spider)
        else:
            spider.logger.info(f'{pipeline_name} skipping')
            return item

    return wrapper



class CleaningPipeline():

    def __init__(self):
        self._cleaning = {
            'Job': self._clean_job,
            'Company': self._clean_company,
        }

        self.job_areas = [ t[0] for t in Job.AREA_CHOICES]

    def clean_string(self, string, clean_end_point=False):
        print('#clean_string: %s' % string)
        try:
            remap = {
                ord('\r'): None,
                ord('\t'): " ",
                ord('\f'): " ",
                ord('\n'): " ",
            }
            clean_string =  string.translate(remap)
            clean_string = clean_string.strip()
            if clean_end_point and clean_string.endswith('.'):
                clean_string = clean_string[:-1]
        except Exception as e:
            clean_string = ''
        return clean_string

    def clean_string_list(self, some_list):
        return list(map(lambda e: e.strip(), some_list))

    def _clean_url(self, pathname_or_href):
        origin = 'https://www.infoempleo.com'
        href = pathname_or_href
        try:
            if pathname_or_href == origin or not pathname_or_href:
                href = ''
            elif pathname_or_href and not ('http' in pathname_or_href):
                href = origin + pathname_or_href
        except Exception as e:
            print('Error in CleanupPipeline._clean_url(%s): %s'%(href,e))
            href = ''
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
            l = get_text_between_parenthesis(string)
            if l and len(l[-1]) > 3:
                province = l[-1]
            else:
                province = string or ''
            return province
        except TypeError as e:
            return ''

    def _clean_location(self, string):
        try:
            write_in_a_file(f'CleanPipeline._clean_location({string})', {}, 'pipeline.txt')
            city = get_text_before_parenthesis(string) or string
            parenthesis = get_text_between_parenthesis(string)
            if parenthesis and len(parenthesis[0]) < 4:
                # Bercial (el) -> el Bercial
                city = parenthesis[0].capitalize() + " " + city
            if city and city.isupper():
                city = city.title()
            alrededores = re.compile(r'(a|A)ldedores (de )?|(a|A)lredores (de )?|(a|A)lredor (de )?|(a|A)lrededores (de )?|(a|A)ldedor (de )?|(a|A)lrededor (de )?')
            city = alrededores.sub('', city)
            city = city.replace('.', "").replace('-', "").replace('etc', "")
            return city.strip()
        except Exception as e:
            return ''

    def _clean_cities(self, string):
        cities = get_a_list_of_enumerates_from_string(string)
        clean_cities = []
        for city in cities:
            clean_city = self._clean_location(city)
            if clean_city:
                clean_cities.append(clean_city)
        return  clean_cities

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
        - Si es una oferta internacional (/ofertas-internacionales/) devuelve 'internacional'
        - Si es no una oferta inernacional devuelve 'nacional'
        :param string:
        :return: "international" or "nacional"
        """
        if 'extranjero' in string:
            return "internacional"
        else:
            return "nacional"

    def _clean_job_date(self, string):
        today = datetime.date.today()
        try:
            number = get_int_from_string(string)
            job_date = today
            if 'dia' in string or 'día' in string or 'hora' in string:
                days = int(number/24) if 'hora' in string else number
                job_date = today - relativedelta(days=days)
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
        """
        Look for two numbers in salary argument and return both
        If only a number is in the string return this value twice
        If there isn't any number return None twice
        :param salary: a string
        :return: two integers
        """
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
        area = area.replace('Area de', "").replace('Área de', "").strip()
        return area

    def _get_annual_salary(self, text):
        """
        Look for a number in the argument 'text' that refers to a salary
        :param text: a string
        :return: an integer refer to the b/y salary
        """
        KEYS = {
            'year': ['bruto anual', 'b/a', 'bruto al año'],
            'month': ['bruto mensual', 'b/m', 'bruto al mes'],
            'day': ['bruto al día', 'b/d', 'bruto al dia'],
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
        summary = item['_summary']
        summary_list = re.split('-', summary)
        summary_list = self.clean_string_list(summary_list)
        experience = self._get_experience(summary_list)
        item['minimum_years_of_experience'], item['recommendable_years_of_experience'] = self._clean_experience(experience)
        salary = self._get_salary(summary_list)
        item['minimum_salary'], item['maximum_salary'] = self._clean_salary(salary)
        if not item['minimum_salary']:
            # Looking for salary in "it_is_offered"
            item['minimum_salary'], item['maximum_salary'] = self._get_annual_salary(item['it_is_offered'])
        working_day = self._get_working_day(summary_list)
        item['working_day'] = self._get_working_day(summary_list)# self._clean_working_day(working_day)
        contract = self._get_contract(summary_list)
        item['contract'] = self._get_contract(summary_list)# self._clean_contract(contract)
        item['_experience'] = experience
        item['_salary'] = salary
        item['_working_day'] = working_day
        item['_contract'] = contract
        return summary_list

    def _clean_job_date_from_state(self, item):
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

    def _clean_company_name(self, company_item):

        def _get_company_name_in_resume(resume):
            try:
                match = re.search(r'S.(L|A)|S.l.u| slu| S(L|A)', resume)
                result = resume if (match or resume.isupper()) else ''
            except:
                result = ""
            return result

        def _get_company_name_in_description(description):

            def _get_company_name_from_description_start(string):
                words = string.split(" ")
                result = []
                for word in words:
                    if word.islower() or word == "Para":
                        break
                    elif (word.istitle() and word not in ["En", 'Desde', 'Somos']) or word.isupper():
                        result.append(word)
                if result and len(result) > 1:
                    return " ".join(result)
                else:
                    return ""

            # Comprobamos si hay algun indicio de que aparezca el nombre de la empresa
            to_search = [' es una empresa', ' es una compañía', ', empresa ', ', Empresa ', ', compañía ',
                         ', Compañía ']
            index = 0
            for i in to_search:
                try:
                    index = description.index(i)
                    break
                except:
                    index = 0
            result = ''
            if index:
                if result.startswith('Para '):  # Para Cantabria, Empresa dedicada al sector...
                    return ''
                # Nos quedamos com la parte inicial de la descripción donde puede estar el nombre de la empresa
                result = description[0:index]
                # Hacemos una limpieza del final de la cadena resultante
                result = result[0:-1] if result.endswith(',') else result
                to_search = ['\n', '\t', '\r']
                for i in to_search:
                    try:
                        index = result.index(i)
                        break
                    except:
                        index = 0
                if index:
                    result = result[0:index]
                result = result.strip()
                # Obtenemos el nombre buscando las palabras que empiecen por mayúscula
                result = _get_company_name_from_description_start(result)
            return result

        name = ''
        if not company_item.get('link') and not company_item.get('is_registered'):
            name = _get_company_name_in_resume(company_item.get('resume')) if company_item.get('resume') else ''
            if not name:
                name = _get_company_name_in_description(company_item.get('description')) if company_item.get('description') else ''
        elif company_item.get('name'):
            name = self.clean_string(company_item.get('name'))
            translate_map = {
                'Ã¡': 'á',
                'Ã ': 'à',
                'Ã‰': 'É',
                'Ã©': 'é',
                'Ã­': 'í',
                'Ã': 'Í',
                'Ã³': 'ó',
                'Ã–': 'Ö',
                'Ã“': 'Ó',
                'Ãš': 'Ú',
                'Ã‘': 'Ñ',
                'Ã±': 'ñ',
            }
            for k, v in translate_map.items():
                name = name.replace(k, v)
        return name

    def _clean_company_description(self, description):
        """
        Clean from the description the empty spaces from the start an the end.
        If the word 'Revisa' is in the description the function returns '' because the description has no meaning.
        :param description: a string
        :return: a string
        """
        try:
            return '' if 'Revisa' in description else self.clean_string(description)
        except:
            return ''

    def _clean_company_category(self, company_item):

        def _get_company_category_in_resume(resume):
            result = ""
            try:
                result = re.sub(
                    r"(((Importante|Destacada|Reconocida|Gran) )?empresa (l(i|í)der )?(dedicada )?((en|de|a) (el|la|los|las)|del|de|al) )", "", resume, flags=re.I)
                if result != resume:
                    result = result.replace('.', '').strip()
                    result_lower = result.lower()
                    result = '' if (result_lower == 'sector' or "nacional" in result_lower) else result
                else:
                    result = ""
            except:
                pass
            return result

        def _get_company_category_in_description(desc):

            def clean_final_coma(string):
                return string[0:-1] if string.endswith(',') else string

            category = ""
            to_search = ['Empresa', 'empresa', 'Compañía', 'compañía']
            index = -1
            for i in to_search:
                try:
                    index = desc.index(i)
                    break;
                except:
                    index = -1
            if index >= 0:
                category_text = desc[index + len(i) + 1:]
                len_category_text = len(category_text)
                to_search = ['Zona', ' ubicada', ' zona', 'centro', 'Centro', 'oficina', ';', 'província', 'provincia',
                             'ciudad', 'Comunidad', ':', '.', '\n', '\t', '\r']
                index = len_category_text
                for i in to_search:
                    try:
                        aux_index = category_text.index(i)
                    except:
                        aux_index = len_category_text
                    finally:
                        index = aux_index if aux_index < index else index
                category_text = category_text[0:index]
                category_text = category_text.replace('España', "").replace('Española', "")
                words = category_text.split(" ")
                count = 0
                result = []
                aux = []
                init_count = False
                coma_found = False
                location_found = False
                prohibited_words = ['Líder', 'Lider', 'Dedicada', "Nacional", "Multinacional"]
                for word in words:
                    count += 1
                    if aux and aux[-1] in ['en', 'para'] and (word.istitle() or word.isupper()):  # 'xxxx en Segovia'
                        aux.pop()
                        location_found = True
                        break
                    elif (word.istitle() or word.isupper()) and (not word in prohibited_words):
                        if aux and (not init_count):
                            aux = []
                        elif aux:
                            for i in aux:
                                result.append(i)
                            aux = []
                        aux_word = clean_final_coma(word)
                        coma_found = aux_word != word
                        result.append(aux_word)
                        init_count = True
                    elif init_count and (not coma_found) and (not word in prohibited_words):
                        aux_word = clean_final_coma(word)
                        coma_found = aux_word != word
                        aux.append(aux_word)
                    elif word in ["en", 'para'] and not init_count:
                        aux.append(word)
                    elif not init_count:
                        aux = []
                    if len(aux) >= 3 or coma_found:
                        break
                if aux and (len(aux[-1]) > 4) and (coma_found or location_found or count == len(words)):
                    result = result + aux
                if result:
                    category = " ".join(result)
                category = category if (len(category) > 4) or (len(category) >= 2 and category.isupper()) else ''
                category = category if category not in "Sector" else ''
                return category

        if not company_item['link']:
            category = _get_company_category_in_resume(company_item['resume']) if company_item['resume'] else ''
            if not category:
                category = _get_company_category_in_description(company_item['description']) if company_item['description'] else ''
        else:
            category = self.clean_string(company_item['category'], True)
        return category

    def _clean_company(self, item):
        item['name'] = self._clean_company_name(item)
        if item.get('is_registered'):
            item['is_registered'] = True
        else:
            item['is_registered'] = True if item.get('link') else False
        item['link'] = self._clean_url(item.get('link'))
        item['resume'] = self.clean_string(item.get('resume'))
        item['description'] = self._clean_company_description(item.get('description'))
        item['category'] = self._clean_company_category(item)
        item['offers'] = get_int_from_string(item.get('offers'), 0)
        item['_location'] = self._clean_location(item.get('_location'))
        print('EXIT _clean_company')  # %
        return item

    def _clean_job(self, item):
        item['name'] = self.clean_string(item['name'])
        item['functions'] = self.clean_string(item['functions'])
        item['requirements'] = self.clean_string(item['requirements'])
        item['it_is_offered'] = self.clean_string(item['it_is_offered'])
        item['state']= self._clean_state(item['state'])
        item['type'] = self._clean_job_type(item['type'])
        item['_summary'] = self._clean_summary(item)
        item['area'] = self._clean_area(item['area'])
        item['id'] = get_int_from_string(item['id'])
        item['vacancies'] = get_int_from_string(item['vacancies'])
        item['registered_people'] = get_int_from_string(item['registered_people'])
        item['_province'] = self._clean_province(item['_province'])
        item['_cities'] = self._clean_cities(item['_cities'])
        item = self._clean_job_date_from_state(item)
        item['nationality'] = self._clean_nationality(item['nationality'])
        if item['nationality'] == "nacional":
            item['_country'] = 'España'
        else:
            item['_country'] = self._clean_country(item['_country'])
        item['expiration_date'] = get_date_from_string(item['expiration_date'])
        item['_languages'] = get_languages_and_levels_pairs(item['requirements'])
        try:
            company = item['company']
            item['company'] = self._cleaning[company.get_model_name()](company)
        except Exception as e:
            print(e)
            save_error(e, { 'pipeline': 'CleanPipeline', 'id':item.get('id'), 'link': item.get('link'), 'item': item})
        return item

    #@check_spider_pipeline
    def process_item(self, item, spider):
        try:
            clean_item = self._cleaning[item.get_model_name()](item)
            return clean_item
        except Exception as e:
            save_error(e, { 'pipeline':'CleanPipeline', 'id':item.get('id'), 'link':item.get('link'), 'item':item })
            return item


class StoragePipeline(object):

    def __init__(self):
        self._storage= {
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

    def _get_item_without_temporal_fields(self, item):
        def drop_keys_that_starts_with(c, d):
            keys_to_delete = [key for key in d.keys() if key.startswith(c)]
            for key in keys_to_delete:
                del d[key]
            return d
        item_ =  item.get_dict_deepcopy()
        item_ = drop_keys_that_starts_with('_', item_)
        return item_

    def _get_languages(self, language_and_level_tuples):
        languages = []
        for language, level in language_and_level_tuples:
            language, is_new_language = Language.objects.get_or_create(name=language, level=level)
            languages.append(language)
        return languages

    def _get_city(self, city_name, province=None, country=None):
        write_in_a_file('StorePipeline._get_city', {'city_name': city_name + '.', 'province':province, 'country': country}, 'pipeline.txt')
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
            # second search with icontains
            if cities_qs:
                city = cities_qs[0]
            else: # not iexact city found
                if province:
                    cities_qs = City.objects.filter(country=country, province=province, name__icontains=city_name)
                else:
                    cities_qs = City.objects.filter(country=country, name__icontains=city_name)
                if cities_qs.count() > 1:
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
        elif country and (city_name.lower() == country.name.lower() or city_name.lower() == get_acronym(country.name).lower()):
            return None
        elif country : # a foreign city:
            print('a foreign city')
            cities_qs = City.objects.filter(name__iexact=city_name,  country=country)
            if cities_qs:
                city = cities_qs[0]
            else:
                city, is_a_new_city = City.objects.get_or_create(name=city_name, country=country)
        else:
            write_in_a_file('StorePipeline._get_city',
                            {'if':'not country'}, 'pipeline.txt')
            try:
                cities_qs = City.objects.filter(name__iexact=city_name)
            except Exception as e:
                write_in_a_file('StorePipeline._get_city',
                                {'city_name': city_name + '.', 'error': e}, 'pipeline.txt')
            write_in_a_file('StorePipeline._get_city',
                            {'cities_qs': str(cities_qs)}, 'pipeline.txt')
            if not cities_qs:
                write_in_a_file('StorePipeline._get_city',
                                {'if': 'not cities_qs'}, 'pipeline.txt')
                cities_qs = City.objects.filter(name__contains=city_name) # contains to avoid coincidence in the middle of the string
                if cities_qs and cities_qs.count() > 1:
                    cities_qs = cities_qs.filter(name__icontains='/')
                    cities = None
                    for city in cities_qs:
                        cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                    cities_qs = cities
                if cities_qs:
                    city = cities_qs[0]
            elif  cities_qs.count() == 1:
                write_in_a_file('StorePipeline._get_city',
                                {'if': 'cities_qs.count() == 1'}, 'pipeline.txt')
                city = cities_qs[0]
        write_in_a_file('StorePipeline._get_city',
                        {'city': city}, 'pipeline.txt')
        return city

    def _get_country (self, country_name):
        if country_name:
            try:
                return Country.objects.get(slug=slugify(country_name))
            except Exception as e:
                pass

    def _get_location(self, city_names, province_name, country_name):
        country = None
        province = None
        if country_name:
            country, is_a_new_country = Country.objects.get_or_create(name=country_name)
        try:
            provinces = Province.objects.filter(name__iexact=province_name)
            province = provinces[0]
        except Exception as e:
            pass
        cities = []
        for city_name in city_names:
            cities.append(self._get_city(city_name, province, country))
        # Deleting the null cities:
        cities = list(filter(lambda c: c, cities ))
        print('#_get_location return: %s %s %s'%(cities, province, country))
        return cities, province, country

    def _get_company_upgrade(self, company, item):
        """
        Checks for any change in the company description, resume and number of offers

        :param company: Company
        :param item: CompanyItem
        :return: a boolean
        """
        upgrade = {}
        if item.get('description') and company.description != item.get('description'):
            upgrade['description'] = item.get('description')
        if item.get('resume')and company.resume != item.get('resume'):
            upgrade['resume'] = item.get('resume')
        if item.get('offers') and company.offers != item.get('offers'):
            upgrade['offers'] = item.get('offers')
        if item.get('is_registered') and not company.is_registered:
            upgrade['is_registered'] = True
        if item.get('link') and not company.link:
            upgrade['link'] = item.get('link')
        area = item.get('area')
        if area and not company.area:
            upgrade['area'] = item.get('area')
        elif area and area not in company.area:
            upgrade['area'] = company.area + [area]
        if item.get('category') and company.category != item.get('category'):
            upgrade['category'] = item.get('category')
        return upgrade

    def _update_company(self, company, item):
        upgrade = self._get_company_upgrade(company, item)
        if upgrade:
            id = company.id
            qs = Company.objects.filter(id=id)
            qs.update(**upgrade)
            company = qs[0]
        return company

    def _store_company(self, item):
        city = self._get_city(item.get('_location'))
        country = city.country if city else self._get_country(item.get('_location'))
        company_dict = self._get_item_without_temporal_fields(item)
        company_dict.setdefault('created_at', timezone.now())
        company_dict.setdefault('city', city)
        company_dict.setdefault('country', country)
        company = None
        # Can be companies with different name and same link
        # A company can have different links but always the same reference
        try:
            if company_dict['name']:
                company_name = company_dict['name']
                company, is_a_new_company_created = Company.objects.get_or_create(slug=slugify(company_name), defaults=company_dict)
            else:
                is_a_new_company_created = False
                qs =  Company.objects.filter(name="").annotate(desc_len=Length('description'))
                qs1 = qs.filter(desc_len__gt=70).filter(description__iexact=company_dict['description'])
                if qs1:
                    company = qs1[0]
                else: # for descriptions length under 70 the resume is too compared
                    qs2 = qs.filter(desc_len__lte=70).filter(description__iexact=company_dict['description'])
                    if qs2 :
                        for c in qs2:
                            if c.resume == company_dict['resume']:
                                company = c
                                break
                    if not company:
                        is_a_new_company_created = True
                        company = Company(**company_dict)
                        company.save()
            if not is_a_new_company_created:
                self._update_company(company, item)
        except Exception as e:
            save_error(e, { 'pipeline':'StorePipeline','company_id': item['name'], 'company_link': item.get('link')})
        print('EXIT STORE_COMPANY') #%
        return company

    def _set_location(self, job, item):
        cities, province, country = self._get_location(item['_cities'], item['_province'], item['_country'])
        job.country = country
        job.province = province
        job.cities.clear()
        job.cities.set(cities)
        return job

    def _set_languages(self, job, item):
        languages = self._get_languages(item.get('_languages'))
        job.languages.clear()
        job.languages.set(languages)
        return job

    def _has_been_the_job_updated(self, job, item):
        """
        # Checks for any change in the offer
        :param job: Job
        :param item: JobItem
        :return: Boolean
        """
        updated = (
            (item['state'] == Job.STATE_UPDATED) and (item['last_update_date'] != job.last_update_date) or
            (item['state'] in [Job.STATE_CREATED, Job.STATE_WITHOUT_CHANGES]) and (item['first_publication_date'] != job.first_publication_date) or
            (item['state'] == Job.STATE_CLOSED) and (item['expiration_date'] != job.expiration_date)
        )
        if (not updated) and (item['state'] == Job.STATE_CLOSED) and (job.state != Job.STATE_CLOSED):
            updated = (
                job.vacancies != item['vacancies'] or
                job.type != item['type'] or
                job.contract != item['contract'] or
                job.working_day != item['working_day'] or
                job.minimum_years_of_experience != item['minimum_years_of_experience'] or
                job.recommendable_years_of_experience != item['recommendable_years_of_experience'] or
                job.minimum_salary != item['minimum_salary'] or
                job.maximum_salary != item['maximum_salary'] or
                job.functions != item['functions'] or
                job.requirements != item['requirements'] or
                job.it_is_offered != item['it_is_offered'] or
                job.area != item['area'] or
                job.category_level != item['category_level']
            )
        return updated

    def _update_job(self, job, item):
        # if job.last_update_date != item['last_update_date']: -> Actualizamos cuando la oferta ha caducado (por si no hemos hecho scraping  sobre una actualización)
        if self._has_been_the_job_updated(job, item):
            job_dict = copy.deepcopy(self._get_item_without_temporal_fields(item))
            job_dict.pop('id', None)
            if item['state'] == Job.STATE_CLOSED:
                job_dict.pop('first_publication_date', None)
                job_dict.pop('last_update_date', None)
            elif item['state'] == Job.STATE_UPDATED:
                job_dict.pop('first_publication_date', None)
            id = job.id
            qs = Job.objects.filter(id=id)
            qs.update(**job_dict)
            job = qs[0]
            self._set_location(job, item)
            self._set_languages(job, item)
            job.save()
        if job.registered_people != item['registered_people']:
            job.registered_people = item['registered_people']
            job.save()
        if job.state != item['state']:
            job.state = item['state']
            job.save()

    def _store_job(self, item):
        try:
            company = item['company']
            item['company'] = self._storage[company.get_model_name()](company)
        except Exception as e:
            save_error(e, { 'pipeline':'StorePipeline', 'company_id': item['name'], 'company_link': item.get('link'), 'item': item})
        job_dict = copy.deepcopy(self._get_item_without_temporal_fields(item))
        job_id = job_dict.pop('id', None)
        job, is_new_item_created = Job.objects.get_or_create(id=job_id, defaults=job_dict)
        if not is_new_item_created:
            self._update_job(job, item)
        else:
            self._set_location(job, item)
            self._set_languages(job, item)
            job.save()
        return job

    #@check_spider_pipeline
    def process_item(self, item, spider):
        try:
            self._storage[item.get_model_name()](item)
            return item
        except Exception as e:
            save_error(e, { 'pipeline':'StorePipeline', 'model':item.get_model_name() , 'line':723, 'id':item.get('id'), 'link':item.get('link'), 'item': item})
            return item
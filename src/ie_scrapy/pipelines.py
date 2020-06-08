# -*- coding: utf-8 -*-

from django import db
from django.utils import timezone
from django.utils.text import slugify
from django.db.utils import InterfaceError
from django.db.models.functions import Length
from dateutil.relativedelta import relativedelta
import copy
import functools
import re
import time
import datetime
import os
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

)
import logging
logging.getLogger().setLevel(logging.INFO)


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
            logging.exception(f'Error: _clean_url({pathname_or_href})')
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
            return country.strip()
        except TypeError as e:
            return ''

    def _clean_province(self, string):
        try:
            l = get_text_between_parenthesis(string)
            if l and len(l[-1]) > 3:
                province = l[-1]
            else:
                province = string or ''
            return province.strip()
        except TypeError as e:
            return ''

    def _clean_location(self, string):
        try:
            city = get_text_before_parenthesis(string) or string
            parenthesis = get_text_between_parenthesis(string)
            if parenthesis and len(parenthesis[0]) < 4:
                city = parenthesis[0].capitalize() + " " + city
            if city and city.isupper():
                city = city.title()
            alrededores = re.compile(
                r'((a|A)ldedores|(a|A)lredores|(a|A)lredor|(a|A)lrededores|(a|A)ldedor|(a|A)lrededor|'
                r'(c|C)erca|(d|D)iversas (ciudades|localidades|ubicaciones))'
                r'( )?(de |del |en el |en |por tod(a|o) )?(((s|S)ur|(n|N)orte|(e|E)ste|(o|O)este|(c|C)entro) de )?')
            city = alrededores.sub('', city)
            city = city.replace('etc.', "").replace('etc', "").replace("Extranjero", "").replace("extranjero", "").strip()
            city = '' if len(city) == 1 else city # city.replace('.', "").replace('-', "")
            return city
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

    def _clean_job_type_(self, url):
        """
                Deprecated
        """
        try:
            return re.findall('ofertas-internacionales|primer-empleo|trabajo', url)[0]
        except Exception:
            return ''

    def _clean_state(self, string):
        if string:
            states = [Job.STATE_CREATED, Job.STATE_UPDATED, Job.STATE_CLOSED]
            states_coincidences = get_coincidences(string, states)
            if states_coincidences:
                return states_coincidences[0]
        return Job.STATE_WITHOUT_CHANGES

    def _clean_nationality(self, string):
        """
        Comprueba la cadena de caracteres que recibe:
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
        today = timezone.localtime(timezone.now()).date()
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
    def _get_working_day(self, summary_list):
        return self._get_specify_info_from_summary_list('jornada', summary_list)

    def _clean_working_day(self, working_day):
        """
        Deprecated
        """
        return get_text_after_key('jornada', working_day)

    def _get_contract(self, summary_list):
        return self._get_specify_info_from_summary_list('contrato', summary_list)

    def _clean_contract(self, contract):
        """
        Deprecated
        """
        return get_text_after_key('contrato', contract)

    def _clean_area(self, area):
        area = area.replace('Area de', "").replace('Área de', "").strip()
        return area

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

    def _clean_salary(self, salary, check=False):
        """
        Look for the maximum and minimum salary in a salary argument and return both
        If only a number is in the string return this value twice
        If there isn't any number return None twice
        The function check both values have the same length (the maximum length)
        :param salary: a string
        :param check: a boolean. Check that all numbers belong to the same unit time(b/a, b/m ...)
        :return: two integers (minimum and maximum salary)
        """
        money = get_int_list_from_string(salary)
        if len(money) > 1 and check:
            ii = [salary.find(' a '), salary.find(' o '), salary.find(' y ')]
            ii = [i for i in ii if i > -1]
            # get the position of the first occurrence or the half
            i = ii[0] if ii else int(len(salary) / 2)
            money_on_the_left = get_int_list_from_string(salary[0:i])
            money_on_the_right = get_int_list_from_string(salary[i:len(salary)])
            max_money = max(*money)
            money_on_the_left = [i for i in money_on_the_left if i * 7 >= max_money]
            money_on_the_right = [i for i in money_on_the_right if i * 7 >= max_money]
            money_on_the_left = [money_on_the_left[-1]] if money_on_the_left else []
            money_on_the_right = [money_on_the_right[0]] if money_on_the_right else []
            money = money_on_the_left + money_on_the_right
        money = (money + money + [None, None])[0:2]
        minimum_salary = money[0]
        maximum_salary = money[1]
        return minimum_salary, maximum_salary

    def _get_annual_salary(self, text):
        """
        Look for numbers in the argument 'text' that refers to a salary
        :param text: a string
        :return: an integer list refer to the b/y minimum and amximum salary
        """
        KEYS = {
            'year': ['b/a', 'bruto/anual', 'brutos/anual', 'bruto anual', 'brutos anual', 'bruto al año',
                     'brutos al año', 'bruto año', 'brutos año', 'anual bruto', 'anuales bruto',
                     'n/a', 'neto/anual', 'netos/anual', 'anual neto', 'anuales neto', 'neto al año', 'netos al año',
                     'neto año', 'netos año', 'neto anual', 'netos anual', ],
            'month': ['b/m', 'bruto/mensual', 'brutos/mensual', 'bruto mensual', 'brutos mensual', 'bruto al mes',
                      'brutos al mes', 'bruto mes', 'brutos mes', 'mensual bruto', 'mensuales bruto',
                      'n/m', 'neto/mes', 'netos/mes', 'mensual neto', 'mensuales neto', 'neto al mes', 'netos al mes',
                      'neto mes', 'netos mes', 'neto mensual', 'netos mensual'],
            'day': ['b/d', 'bruto/día', 'bruto/dia', 'bruto al día', 'bruto al dia', 'bruto día', 'bruto dia',
                    'brutos/día', 'brutos/dia', 'brutos al día', 'brutos al dia', 'brutos día', 'brutos dia', ],
            'hour': ['b/h', 'bruto/hora', 'brutos/hora', 'bruto a la hora', 'brutos a la hora',
                     'n/h', 'neto/hora', 'netos/hora', 'neto a la hora', 'netos a la hora', ],
        }
        KEYS2 = {
            'year': ['año', 'anual'],
            'month': ['mes', 'mensual'],
            'day': ['día', 'dia'],
            'hour': ['hora'],
        }
        salary = [None, None]
        text = text.lower().replace('un/a', '')
        if text:
            salary_type_tl = ([('year', sub, text.rfind(sub)) for sub in KEYS['year'] if text.rfind(sub) > 0] or
                              [('month', sub, text.rfind(sub)) for sub in KEYS['month'] if text.rfind(sub) > 0])
            if salary_type_tl:
                # get the last ocurrence
                salary_type_tl = [salary_type_tl[0]][0]
                # get the text around the ocurrence
                for sentence in reversed(text.splitlines()):
                    if salary_type_tl[1] in sentence:
                        text = sentence
                        # !Important: the new index must be recalculated
                        salary_type_tl = (salary_type_tl[0], salary_type_tl[1], text.rfind(salary_type_tl[1]))
                        break
            else:
                for sentence in reversed(text.splitlines()):
                    if ('salario' in sentence) or ('sueldo' in sentence):
                        text = sentence
                        salary_type_tl = ([('year', sub, text.rfind(sub)) for sub in KEYS2['year'] if text.rfind(sub) > 0] or
                                  [('month', sub, text.rfind(sub)) for sub in KEYS2['month'] if text.rfind(sub) > 0])
                        if salary_type_tl:
                            salary_type_tl = [salary_type_tl[0]][0]
                        break
            if salary_type_tl:
                start = max(0, salary_type_tl[2] - 70)
                end = min(salary_type_tl[2] + 70, len(text))
                text = text[start:end]
                salary = list(self._clean_salary(text, True))
                if salary[0] and salary_type_tl[0] == 'month':
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
        item['working_day'] = self._get_working_day(summary_list)
        item['contract'] = self._get_contract(summary_list)
        return summary_list

    def _get_it_is_offered(self, text):
        offered = ''
        try:
            ii = [
                ('Se ofrece', text.rfind('Se ofrece')),
                ('Te ofrecemos', text.rfind('Te ofrecemos')),
                ('Te ofrece', text.rfind('Te ofrece')),
                ('Ofrecemos',text.rfind('Ofrecemos')),
            ]
            ii = [t for t in ii if t[1] > 0]
            i = ii[0] if ii else None
            if i:
                offered = text[i[1]:len(text)]
                offered = offered.replace(i[0]+':','').replace(i[0],'')
                offered = self.clean_string(offered)
        except Exception as e:
            pass
        return offered

    def _clean_it_is_offered(self, item):
        it_is_offered = self.clean_string(item['it_is_offered'])
        if not it_is_offered:
            it_is_offered = self._get_it_is_offered(item['functions'])
        return it_is_offered

    def _set_job_dates_from_state(self, item):
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

        def _get_important_words(string):
            string = string.replace('Empresa', "").replace('Compañ', "").replace('En', "").replace('Desde', "").replace('Somos', "")
            lsub = string.split(" ")
            lsub = lsub[1:] if lsub[0].istitle() and not lsub[1].istitle() else lsub
            important_words = [x for x in lsub if x.istitle() or x.isupper()]
            sub= (" ").join(important_words)
            return sub

        def _get_company_name_in_resume(resume):
            try:
                if resume.isupper() or resume.startswith('Grupo') or (" " not in resume and sum(1 for c in resume if c.isupper()) > 1):
                    return resume
                else:
                    try:
                        match = re.search(r'S.(L|A)|S.l.u| slu| S(L|A)', resume)[0]
                        i = resume.find(match)
                        sub = resume[0:i]
                        sub_ = _get_important_words(sub)
                        match = match + '.' if '.' in match and not match.endswith('.') else match
                        result = f'{sub_} {match}'
                        return result
                    except:
                        result = ""
            except:
                result = ""
            return result

        def _get_company_name_in_description(description):

            def _get_company_name_from_description_start(string_titled):
                words = string_titled.split(" ")
                words = words[1:] if words[0].istitle() and not words[1].istitle() else words
                string = (" ").join(words)
                i = string.find('Para') # Para Madrid
                string = string[0:i] if i > -1 else string
                words = string.split(" ")
                result = []
                for word in words:
                    if len(result) > 1 and word.islower():
                        break
                    elif (word.istitle() and word not in ["En", 'Desde', 'Somos', 'Empresa', 'Compañía']) or word.isupper():
                        result.append(word[0:-1] if word.endswith(',') else word)
                if result and len(result) > 1:
                    return " ".join(result)
                else:
                    return ""

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
                if result.startswith('Para '):  # 'Para Cantabria, Empresa dedicada al sector...'
                    return ''
                result = description[0:index]
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
                result = _get_company_name_from_description_start(result)
            return result

        name = ''
        if not company_item.get('link') and not company_item.get('is_registered'):
            name = _get_company_name_in_resume(self.clean_string(company_item.get('resume'))) if company_item.get('resume') else ''
            if not name:
                name = _get_company_name_in_description(company_item.get('description')) if company_item.get('description') else ''
        elif company_item.get('name'):
            name = company_item.get('name')
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
        return self.clean_string(name)

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
            if resume.isupper() or resume.istitle():
                return resume
            try:
                rexp=r"(((Importante|Destacada|Reconocida|Gran) )?(empresa |asesoría |consultoría |consultora )(multinacional |nacional )?(l(i|í)der )?(dedicada |dedicada y especializada |especializada )?((en|de|a|al) (el|la|los|las)|del|de|al|en) )"
                result = re.sub(rexp, "", resume, flags=re.I)
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

    def _clean_company_reference(self, link):
        try:
            reference = os.path.basename(os.path.dirname(link))
            reference = int(reference) if reference.isnumeric() else None
        except:
            reference = None
        return reference

    def _clean_company(self, item):
        item['name'] = self._clean_company_name(item)
        if item.get('is_registered'):
            item['is_registered'] = True
        item['link'] = self._clean_url(item.get('link'))
        item['reference'] = self._clean_company_reference(item.get('reference'))
        item['resume'] = self.clean_string(item.get('resume'))
        item['description'] = self._clean_company_description(item.get('description'))
        item['category'] = self._clean_company_category(item)
        item['offers'] = get_int_from_string(item.get('offers'))
        item['_location'] = self._clean_location(item.get('_location'))
        return item

    def _clean_job(self, item):
        item['_summary'] = self._clean_summary(item)
        if not item['minimum_salary']:
            # Looking for salary in "it_is_offered"
            item['minimum_salary'], item['maximum_salary'] = self._get_annual_salary(item['it_is_offered'])
            if not item['minimum_salary']:
                item['minimum_salary'], item['maximum_salary'] = self._get_annual_salary(item['functions'])
        item['name'] = self.clean_string(item['name'])
        item['functions'] = self.clean_string(item['functions'])
        item['requirements'] = self.clean_string(item['requirements'])
        item['it_is_offered'] = self._clean_it_is_offered(item)
        item['state']= self._clean_state(item['state'])
        # item['type'] doesn't need cleaning
        item['area'] = self._clean_area(item['area'])
        item['id'] = get_int_from_string(item['id'])
        item['vacancies'] = get_int_from_string(item['vacancies'])
        item['registered_people'] = get_int_from_string(item['registered_people'])
        item['_province'] = self._clean_province(item['_province'])
        item['_cities'] = self._clean_cities(item['_cities'])
        item = self._set_job_dates_from_state(item)
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
            logging.exception(f'Error: {e}')
        return item

    #@check_spider_pipeline
    def process_item(self, item, spider):
        try:
            clean_item = self._cleaning[item.get_model_name()](item)
            return clean_item
        except Exception as e:
            logging.exception(f'Error: CleaningPipeline.process_item({str(item)})')
            return item


class StoragePipeline(object):

    def __init__(self):
        self.count = 0
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
        def drop_keys_that_starts_with(character, dictionary):
            keys_to_delete = [key for key in dictionary.keys() if key.startswith(character)]
            for key in keys_to_delete:
                del dictionary[key]
            return dictionary
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
        """
        Try to get a city from job.models.City and if the city doesn't exist in the model the function will try to create it.
        If country is equal 'España' the function expects that province argument will not be None.
        If there are more than one city in the model and province argument is None, the city wouldn't be create.
        If the city doesn't exist in the model and country argument is None, the city wouldn't be create.

        :param city_name: a string.
        :param province: job.models.Province
        :param country: Country.models.Province
        :return:
        """
        if not city_name:
            return None
        city = None
        if country and country.name == 'España':
            # first search with iexact
            if province:
                cities_qs = City.objects.filter(country=country, province=province, name__iexact=city_name)
            else:
                cities_qs = City.objects.filter(country=country, name__iexact=city_name)
            if cities_qs and cities_qs.count() > 1:
                return None
            elif cities_qs:
                city = cities_qs[0]
            else: # not iexact city found so second search with icontains
                if province:
                    cities_qs = City.objects.filter(country=country, province=province, name__icontains=city_name)
                else:
                    cities_qs = City.objects.filter(country=country, name__icontains=city_name)
                    try:
                        province = Province.objects.get(name=city_name)
                    except:
                        pass
                if cities_qs.count() > 1:
                    cities_qs = cities_qs.filter(name__icontains='/')
                    cities = []
                    for city in cities_qs:
                        cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                    cities_qs = cities
                if cities_qs:
                    city = cities_qs[0]
                    if province and (city_name == province.name):
                        city = None
                elif province and (city_name != province.name):
                    city = City.objects.create(name=city_name, province=province, country=country)
        elif country and (city_name.lower() == country.name.lower() or city_name.lower() == get_acronym(country.name).lower()):
            return None
        elif country : # a foreign city:
            cities_qs = City.objects.filter(name__iexact=city_name,  country=country)
            if cities_qs and cities_qs.count() > 1:
                return None
            elif cities_qs:
                city = cities_qs[0]
            else:
                city, is_a_new_city = City.objects.get_or_create(name=city_name, country=country)
        else:
            try:
                cities_qs = City.objects.filter(name__iexact=city_name)
            except Exception as e:
                logging.exception(f'Error: {e}')
            if not cities_qs:
                cities_qs = City.objects.filter(name__contains=city_name) # contains to avoid coincidence in the middle of the string
                if cities_qs and cities_qs.count() > 1:
                    cities_qs = cities_qs.filter(name__icontains='/')
                    cities = []
                    for city in cities_qs:
                        cities = [city for name in city.name.split('/') if city_name.lower() == name.lower()]
                    cities_qs = cities
                if cities_qs:
                    city = cities_qs[0]
            elif  cities_qs.count() == 1:
                city = cities_qs[0]
        return city

    def _get_province (self, province_name):
        if province_name:
            qs = Province.objects.filter(name=province_name)
            if not qs:
                qs = Province.objects.filter(slug=province_name)
            return qs[0] if qs else None
        else:
            return None

    def _get_country (self, country_name):
        if country_name:
            qs = Country.objects.filter(name=country_name)
            if not qs:
                qs = Country.objects.filter(slug=country_name)
            return qs[0] if qs else None
        else:
            return None

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
        cities = list(filter(lambda c: c, cities))
        if cities:
            if not country:
                country = cities[0].country
            if not province:
                province = cities[0].province
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
        if item.get('city') and company.city != item.get('city'):
            upgrade['city'] = item.get('city')
        if item.get('province') and company.province != item.get('province'):
            upgrade['province'] = item.get('province')
        if item.get('country') and company.city != item.get('country'):
            upgrade['country'] = item.get('country')
        return upgrade

    def _update_company(self, company, item):
        upgrade = self._get_company_upgrade(company, item)
        if upgrade:
            id = company.id
            qs = Company.objects.filter(id=id)
            qs.update(**upgrade)
            company = qs[0]
        return company

    def _set_locations_from_location(self, item):
        location = item.get('_location')
        city = self._get_city(location)
        country = self._get_country(location)
        province = self._get_province(location)
        if province:
            city = city if city and province.name == city.name else None
            country = province.country
        elif city:
            country = city.country
            province = city.province
        elif not city:
            if not country:
                qs = Country.objects.filter(cities__name__iexact=location) # Example: alamillo of Granada and alamillo of Ciudad Real in Spain
                country_names = [c.name for c in qs]
                country_names = set(country_names)
                country = qs[0] if len(country_names) == 1 else None
            if not province:
                qs = Province.objects.filter(cities__name__icontains=location)
                province_names = [p.name for p in qs]
                province_names = set(province_names)
                province = qs[0] if len(province_names) == 1 else None
                if province:
                    country = province.country
        item['city'] = city
        item['province'] = province
        item['country'] = country

    def _store_company(self, item):
        # INFO: Can be companies with different name and same link
        # INFO: A company can have different links but always the same reference
        self._set_locations_from_location(item)
        company_dict = self._get_item_without_temporal_fields(item)
        company = None
        try:
            if company_dict.get('name'):
                qs = None
                if company_dict.get('reference'):
                    reference = company_dict.get('reference')
                    qs = Company.objects.filter(reference=reference)
                elif company_dict.get('link'):
                    link = company_dict.get('link')
                    qs = Company.objects.filter(link=link)
                if qs:
                    company = qs[0]
                    is_a_new_company_created = False
                else:
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
                Company.objects.filter(id=company.id).update(checked_at=timezone.localtime(timezone.now()))
                company = self._update_company(company, item)
        except Exception as e:
            logging.exception(f'Error: {e}')
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
        # Checks for any change in info of the offer, but not the state.
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
                job.description != item['description'] or
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
        return job

    def _store_job(self, item):
        try:
            company = item['company']
            item['company'] = self._storage[company.get_model_name()](company)
        except Exception as e:
            logging.exception(f'Error: {e}')
        job_dict = copy.deepcopy(self._get_item_without_temporal_fields(item))
        job_id = job_dict.pop('id', None)
        job, is_new_item_created = Job.objects.get_or_create(id=job_id, defaults=job_dict)
        if not is_new_item_created:
            Job.objects.filter(id=job.id).update(checked_at=timezone.localtime(timezone.now()))
            job = self._update_job(job, item)
        else:
            self._set_location(job, item)
            self._set_languages(job, item)
            job.save()
        return job

    #@check_spider_pipeline
    def process_item(self, item, spider):
        self.count = self.count + 1
        try:
            self._storage[item.get_model_name()](item)
            return item
        except Exception as e:
            logging.exception(f'Error: StotagePipelins.process_item{str(item)}')
            return item
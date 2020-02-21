import pandas as pd
import math
from django.db.models import Q
from django.db.models.functions import Length
from .models import Job, City, Province, Community, Country, Language, Company
import sqlite3
import time
from datetime import date
import re

CSV_PATH = 'static/data/csv/'
SUFFIX = '_20200115'
COUNTRIES_CSV = f'{CSV_PATH}country{SUFFIX}.csv'
COMMUNITIES_CSV = f'{CSV_PATH}community{SUFFIX}.csv'
PROVINCES_CSV = f'{CSV_PATH}province{SUFFIX}.csv'
CITIES_CSV = f'{CSV_PATH}city{SUFFIX}.csv'
#CITIES_CSV = f'{CSV_PATH}cities 06112019.csv'

BLANK_COLUMN = 'Unnamed: 0'

def get_df(path):
    df = pd.read_csv(path)
    try:
        df.drop([BLANK_COLUMN], axis=1, inplace=True)
    except:
        pass
        df.dropna(how='all', axis=1, inplace=True)
    return df

def insert_countries(countries_csv=COUNTRIES_CSV):
    Country.objects.all().delete()
    entries = []
    countries_df = get_df(countries_csv)
    for e in countries_df.T.to_dict().values():
        entries.append(Country(**e))
    Country.objects.bulk_create(entries)

def insert_communities(communities_csv = COMMUNITIES_CSV):
    Community.objects.all().delete()
    entries = []
    provinces_df = get_df(communities_csv)
    for e in provinces_df.T.to_dict().values():
        country_id = e['country_id']
        country = Country.objects.get(id=country_id)
        e['country'] = country
        entries.append(Community(**e))
    Community.objects.bulk_create(entries)

def insert_provinces(provinces_csv=PROVINCES_CSV):
    Province.objects.all().delete()
    entries = []
    provinces_df = get_df(provinces_csv)
    spain = Country.objects.filter(name="España")[0]
    for e in provinces_df.T.to_dict().values():
        e['country'] = spain
        entries.append(Province(**e))
    Province.objects.bulk_create(entries)


def insert_cities(cities_csv=CITIES_CSV):
    City.objects.all().delete()
    entries = []
    cities_df = get_df(cities_csv)
    cities_df.drop(['slug'], axis=1, inplace=True)
    cities_df.dropna(how='any', inplace=True)
    for e in cities_df.T.to_dict().values():
        country_id = e['country_id']
        if country_id and (not math.isnan(country_id)):
            try:
                country = Country.objects.get(id=int(country_id))
                e['country'] = country
            except Exception as e:
                print(f'Error "{e}"  in country_id:{country_id}')
                continue
        else:
            continue
        province_id = e['province_id']
        if province_id and (not math.isnan(province_id)):
            try:
                province = Province.objects.get(id=int(province_id))
                e['province'] = province
            except Exception as e:
                print(f'Error "{e}" in province_id:{province_id}')
                e['province'] = None
        else:
            e['province'] = None
        entries.append(City(**e))
    City.objects.bulk_create(entries)
    spain = Country.objects.get(name="España")
    City.objects.get_or_create(name='Ceuta', defaults={'country': spain})
    City.objects.get_or_create(name='Melilla', defaults={'country': spain})


def delete_locations():
    Country.objects.all().delete()
    Community.objects.all().delete()
    Province.objects.all().delete()
    City.objects.all().delete()


def insert_locations():
    delete_locations()
    insert_countries()
    insert_communities()
    insert_provinces()
    insert_cities()

def create_languages():
    for l in Language.LANGUAGES:
        for l_ in Language.LEVELS:
            Language.objects.get_or_create(name=l, level=l_)


def delete_cities_with_spaces():
    qs = City.objects.all()
    for city in qs:
        if city.name != city.name.strip():
            city.delete()

def sql():
    DB = "db.sqlite3"
    connection = sqlite3.connect(DB)
    curr = connection.cursor()
    #data = curr.execute("""ALTER TABLE job_job ADD 'first_publication_date' date DEFAULT NULL""")
    #data = curr.execute("""ALTER TABLE job_job ADD 'last_update_date' date DEFAULT NULL""")
    data = curr.execute("""ALTER TABLE job_job ADD 'state' varchar(20) DEFAULT NULL""")
    #data = curr.execute("""CREATE TABLE  IF NOT EXISTS job_sub (name text)""")
    connection.commit()
    connection.close()


def fix_jobs_state():
    exp_qs = Job.objects.filter(expiration_date__lte=date.today())
    for job in exp_qs:
        job.state = Job.STATE_CLOSED
        job.save()

def fix_state_update_date():
    qs = Job.objects.filter(last_update_date=None)
    qs = qs.exclude(first_publication_date=None)
    for job in qs:
        job.last_update_date = job.first_publication_date
        job.save()

def save_model_csv(model):
    today = date.today()
    qs = model.objects.all()
    df = pd.DataFrame.from_records(qs.values())
    name = CSV_PATH + model.__name__.lower() + '_' + today.strftime('%Y%m%d') + '.csv'
    df.to_csv(name, index=False)

def save_models_to_csv():
    models = [
        Job,
        City,
        Company,
        Country,
        Province,
        Community,
        Language
    ]
    for model in models:
        save_model_csv(model)


def set_province_and_country_in_national_jobs():
    qs = Job.objects.filter(Q(type=Job.TYPE_NATIONAL) | Q(type=Job.TYPE_FIRST_JOB)).filter(province=None)
    for job in qs:
        try:
            city = job.cities.all().first()
            province = city.province
            country = city.country
            job.province = province
            job.country = country
            job.save()
        except:
            pass

def set_province_and_country_in_national_jobs2():
    qs = Job.objects.filter(Q(type=Job.TYPE_NATIONAL) | Q(type=Job.TYPE_FIRST_JOB)).filter(province=None)
    for job in qs:
        try:
            province = Province.objects.get(name=job.provincename)
            job.province = province
        except:
            pass
        try:
            country = Country.objects.get(name=job.countryname)
            job.country = country
        except:
            pass
        job.save()

def set_Ceuta_Melilla():
    qs = Job.objects.filter(Q(provincename="Ceuta") | Q(provincename="Melilla")).filter(cities=None)
    ceuta = City.objects.get(name="Ceuta")
    melilla = City.objects.get(name="Melilla")
    cities = []
    for job in qs:
        if job.provincename == "Ceuta":
            cities.append(ceuta)
        elif job.provincename == "Melilla":
            cities.append(melilla)
        else:
            pass
        job.cities.clear()
        job.cities.set(cities)
        job.save()


def delete_some_jobs_by_link():
    job_urls = [
        'https://www.infoempleo.com/ofertasdetrabajo/ingeniero-de-certificacion-de-maquinaria-hm/barcelona/2563199/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/lleida/2569681/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/murcia/2569683/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/palencia/2569684/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/ourense/2569687/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/salamanca/2569686/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/jaen/2569688/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/santa-cruz-de-tenerife/2569689/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/pontevedra/2569685/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/soria/2569690/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/valencia/2569694/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/toledo/2569693/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/tarragona/2569691/',
        'https://www.infoempleo.com/ofertasdetrabajo/lider-de-red-de-ventas-sector-venta-directa-de-productos-de-belleza/sevilla/2569695/',
    ]

    for link in job_urls:
        try:
            j = Job.objects.get(link=link)
            j.delete()
        except:
            pass

def delete_some_jobs_without_company_name():
    job_urls = Job.objects.filter(company__company_name="")
    job_urls = [
        'https://www.infoempleo.com/ofertasdetrabajo/coordinadora-export/guipuzcoa/2581201/',
        'https://www.infoempleo.com/ofertasdetrabajo/export-manager/guipuzcoa/2581221/',
        'https://www.infoempleo.com/ofertasdetrabajo/directora-desarrollo-negocio/guipuzcoa/2581360/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnicoa-prevencion-de-riesgos-laborales/guipuzcoa/2583325/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnicoa-calidad/guipuzcoa/2583120/',
        'https://www.infoempleo.com/ofertasdetrabajo/coordinadora/vizcaya/2584559/',
        'https://www.infoempleo.com/ofertasdetrabajo/administrativoa-contable/guipuzcoa/2582900/',
        'https://www.infoempleo.com/ofertasdetrabajo/directora-consultoria-tecnica/guipuzcoa/2582110/',
        'https://www.infoempleo.com/ofertasdetrabajo/customer-assistant/guipuzcoa/2581633/',
        'https://www.infoempleo.com/ofertasdetrabajo/comercial-repuestos-automocion/guipuzcoa/2585618/',
        'https://www.infoempleo.com/ofertasdetrabajo/ingenieroa-calidad/guipuzcoa/2578710/',
        'https://www.infoempleo.com/ofertasdetrabajo/directora-gestion-personas/guipuzcoa/2578778/',
        'https://www.infoempleo.com/ofertasdetrabajo/gestora-mantenimiento/alava/2579634/',
        'https://www.infoempleo.com/ofertasdetrabajo/directora-gerente/guipuzcoa/2578713/',
        'https://www.infoempleo.com/ofertasdetrabajo/responsable-de-calidad-automocion/vizcaya/2576890/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnicoa-administracion-laboral/guipuzcoa/2575814/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnicoa-contable/guipuzcoa/2577794/',
        'https://www.infoempleo.com/ofertasdetrabajo/ayudante-consulta-marketing/guipuzcoa/2576689/',
        'https://www.infoempleo.com/ofertasdetrabajo/responsable-mantenimiento-instalaciones/guipuzcoa/2578712/',
        'https://www.infoempleo.com/ofertasdetrabajo/auxiliar-administrativoa/guipuzcoa/2576454/',
        'https://www.infoempleo.com/ofertasdetrabajo/responsable-aprovisionamientos-y-logistica/guipuzcoa/2578323/',
        'https://www.infoempleo.com/ofertasdetrabajo/ingenieroa-produccion/guipuzcoa/2578316/',
        'https://www.infoempleo.com/ofertasdetrabajo/directora-unidad-negocio/guipuzcoa/2578779/',
        'https://www.infoempleo.com/ofertasdetrabajo/ingenieroa-comercial/alava/2578711/',
        'https://www.infoempleo.com/ofertasdetrabajo/comercial-exportacion/guipuzcoa/2578294/',
        'https://www.infoempleo.com/ofertasdetrabajo/caldereroa/guipuzcoa/2575037/',
        'https://www.infoempleo.com/ofertasdetrabajo/montador-hidraulico-tubero/guipuzcoa/2574631/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnico-de-mantenimiento-mecanico/guipuzcoa/2574208/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnico-de-inyeccion-de-plastico/guipuzcoa/2572347/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnico-de-inyeccion-de-plastico/guipuzcoa/2572338/',
        'https://www.infoempleo.com/ofertasdetrabajo/business-development-manager/guipuzcoa/2575220/',
        'https://www.infoempleo.com/ofertasdetrabajo/export-area-manager/guipuzcoa/2573979/',
        'https://www.infoempleo.com/ofertasdetrabajo/tecnicoa-de-instalaciones-mantenimiento-electronico/vizcaya/2574748/',
    ]

    for link in job_urls:
       try:
           j = Job.objects.get(link=link)
           j.delete()
       except:
           pass

def set_id_in_companies():
    qs = Company.objects.all()
    count = 1
    for c in qs:
        c.id = count
        count += 1
        c.save()

def _get_name_from_company_without_link(company):
    ###################################
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
                elif (word.istitle() and word != "En") or word.isupper():
                    result.append(word)
            if result and len(result) > 1:
                return " ".join(result)
            else:
                return ""

        # Comprobamos si hay algun indicio de que aparezca el nombre de la empresa
        to_search = [' es una empresa', ' es una compañía', ', empresa ', ', Empresa ', ', compañía ', ', Compañía ']
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
            # Nos quedamos com la parte inicial de la descripción donde puede esatr el nombre de la empresa
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

    name = _get_company_name_in_resume(company.resume) if company.resume else ''
    if not name:
        name = _get_company_name_in_description(company.description) if company.description else ''
    return name


def _get_category_from_company_without_link(company):

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

    category = _get_company_category_in_resume(company.resume) if company.resume else ''
    if not category:
        category = _get_company_category_in_description(company.description) if company.description else ''
    return category


def _set_name_and_category_of_companies_without_link():
    qs = Company.objects.filter(link='')
    for c in qs:
        name = _get_name_from_company_without_link(c)
        category = _get_category_from_company_without_link(c)
        c.name = name
        c.category = category
        c.save()
    qs = Company.objects.filter(link=None)
    for c in qs:
        name = _get_name_from_company_without_link(c)
        category = _get_category_from_company_without_link(c)
        c.name = name
        c.category = category
        c.save()

    # Coger category a través de resume
    # Coger category a través de description




def _clean_string(string):
    try:
        clean_string = string.strip()
        if clean_string.endswith('.'):
            clean_string = clean_string[:-1]
    except Exception as e:
        clean_string = ''
    return clean_string


def _unify_sames_companies():
    """
    Para unificar compañias que no tienen nombre pero coinciden en su descripción larga (> 71)
    :return:
    """
    # Cojo las compañias sin nombre y con  una descripcion mayor a 70 y las ordeno por la descripcion
    cc = Company.objects.annotate(desc_len=Length('description')).filter(name="")
    cc = cc.filter(desc_len__gt=71).order_by('description')
    # Creo un conjunto/lista donde guardaré los ids de las compañias repetidas que eliminare
    id_companies_to_delete = set()
    # Itero las compañias
    for c in cc:
        # Compruebo que el id de la compañia no este en el conjunto de compañias revisadas a eliminar
        if not (c.id in id_companies_to_delete):
            # Busco compañias con la misma descripcion
            cc_ = cc.filter(description__iexact=c.description)
            # Si encuentro mas de una compañia, cojo la primera (que será la principal) y el resto la meto en una lista (l = qs[1:])
            if cc_.count() > 1 :
                c_ = cc_[0]
                wrong_cc = cc_[1:]
                # Itero las lista de compañias
                for wc in wrong_cc:
                    # Busco los trabajos con esas compañias y las sustituyo por la compañia principal
                    jj = Job.objects.filter(company__id=wc.id)
                    for j in jj:
                        j.company = c_
                        j.save()
                    id_companies_to_delete.add(wc.id)
    # Introduzco los ids de esas compañias que eliminare al final en el conjunto/lista destiando a ello
    for id_ in id_companies_to_delete:
        c = Company.objects.get(id=id_)
        c.delete()

def clean_test_running_spider():
    import json

    qs = Job.objects.filter(area=Job.AREA_LEGAL)
    qs.delete()

    with open("parsed urls state.json", 'r') as f:
        try:
            d = json.loads(f.read())
        except Exception as e:
            print(f'Error: {e}')
    d['https://www.infoempleo.com/trabajo/area-de-empresa_legal/']['results_parsed'] = 68
    with open("parsed urls state.json", 'w') as f:
        try:
            f.write(json.dumps(d))
        except Exception as e:
            print(f'Error: {e}')

    l = ['tasks.txt', 'tasks_view.txt']
    for sf in l:
        with open(sf, 'w') as f:
            f.write("")

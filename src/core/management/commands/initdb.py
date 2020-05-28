from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import math
import os
import threading
from job.models import City, Province, Community, Country, Language
import logging
logging.getLogger().setLevel(logging.INFO)

class InitializingDataInTablesException(Exception):
    pass

FILE = __file__
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR,'data', 'csv')
SUFFIX = ''
COUNTRIES_CSV = os.path.join(CSV_PATH, f'country{SUFFIX}.csv')
COMMUNITIES_CSV = os.path.join(CSV_PATH, f'community{SUFFIX}.csv')
PROVINCES_CSV = os.path.join(CSV_PATH, f'province{SUFFIX}.csv')
CITIES_CSV = os.path.join(CSV_PATH, f'city{SUFFIX}.csv')

BLANK_COLUMN = 'Unnamed: 0'

ERROR_HELP_MSG = """
    1. Have you configured your database in settings.py?
    2. Have you done the migrations to your database with python manage.py makemigrations and python manage.py migrate?'
"""

def _get_df(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        df = pd.read_csv(path, encoding="ISO-8859-1")
    try:
        df.drop([BLANK_COLUMN], axis=1, inplace=True)
    except:
        pass
    df.dropna(how='all', axis=1, inplace=True)
    return df

def _get_model_df(smodel):
    try:
        path = f'{CSV_PATH}{smodel.lower()}{SUFFIX}.csv'
        return _get_df(path)
    except Exception as e:
        logging.exception(f"Error getting {path}")

def _insert_countries(countries_csv=COUNTRIES_CSV):
    Country.objects.all().delete()
    countries_df = _get_df(countries_csv)
    for e in countries_df.T.to_dict().values():
        Country(**e).save()

def _insert_communities(communities_csv = COMMUNITIES_CSV):
    Community.objects.all().delete()
    provinces_df = _get_df(communities_csv)
    for e in provinces_df.T.to_dict().values():
        country_id = int(e['country_id'])
        country = Country.objects.get(id=country_id)
        e['country'] = country
        Community(**e).save()

def _insert_provinces(provinces_csv=PROVINCES_CSV):
    Province.objects.all().delete()
    provinces_df = _get_df(provinces_csv)
    spain = Country.objects.filter(name="España")[0]
    for e in provinces_df.T.to_dict().values():
        e['country'] = spain
        community = Community.objects.get(id=int(e['community_id']))
        e['community'] = community
        del (e['community_id'])
        Province(**e).save()

def _insert_cities(cities_csv=CITIES_CSV):
    City.objects.all().delete()
    cities_df = _get_df(cities_csv)
    try:
        cities_df.drop(['slug'], axis=1, inplace=True)
    except:
        pass
    cities_df.dropna(how='any', inplace=True)
    for e in cities_df.T.to_dict().values():
        country = None
        country_id = int(e['country_id'])
        if country_id and (not math.isnan(country_id)):
            try:
                country = Country.objects.get(id=int(country_id))
                e['country'] = country
            except Exception as e:
                logging.exception(f'Error "{e}"  in country_id:{country_id}')
                continue
        else:
            continue
        province = None
        province_id = int(e['province_id'])
        if province_id and (not math.isnan(province_id)):
            try:
                province = Province.objects.get(id=int(province_id))
                e['province'] = province
            except Exception as e:
                logging.exception(f'Error "{e}" in province_id:{province_id}')
                continue
        else:
            continue
        del(e['country_id'])
        del(e['province_id'])
        City(**e).save()
    spain = Country.objects.get(name="España")
    City.objects.get_or_create(name='Ceuta', defaults={'country': spain})
    City.objects.get_or_create(name='Melilla', defaults={'country': spain})


def _delete_locations():
    Country.objects.all().delete()
    Community.objects.all().delete()
    Province.objects.all().delete()
    City.objects.all().delete()

def insert_locations():
    _delete_locations()
    _insert_countries()
    _insert_communities()
    _insert_provinces()
    _insert_cities()
    logging.info('The locations tables have been initialized')

def insert_languages():
    Language.objects.all().delete()
    for l in Language.LANGUAGES:
        for l_ in Language.LEVELS:
            try:
                Language.objects.get_or_create(name=l, level=l_)
            except Exception as e:
                logging.exception(f'Error creating language {l}')
    logging.info('The language table has been initialized')

def is_language_table_empty():
    try:
        return Language.objects.all().count() == 0
    except Exception as e:
        message = f"""
               Error: {e}
               {ERROR_HELP_MSG}
               """
        raise InitializingDataInTablesException(f'{message}')

def are_location_tables_empty():
    try:
        return Province.objects.all().count() == 0
    except Exception as e:
        message = f"""
        Error: {e}
        {ERROR_HELP_MSG}
        """
        raise InitializingDataInTablesException(f'{message}')

def initialize_language_table():
    if is_language_table_empty():
        thread = threading.Thread(target=insert_languages)
        thread.start()

def initialize_location_tables():
    if are_location_tables_empty():
        #thread = threading.Thread(target= insert_locations)
        #thread.start()
        insert_locations()

def has_been_the_database_initializing():
    return (not is_language_table_empty()) and (not are_location_tables_empty())

def initialize_database():
    """
    Initialize Language Country, Community, Province, City tables
    """
    if not has_been_the_database_initializing():
        initialize_language_table()
        initialize_location_tables()
    else:
        logging.info('The database has been initialized')

class Command(BaseCommand):
    help = "Initializing language and locations tables"

    def handle(self, *args, **options):
        try:
            initialize_database()
        except Exception as e:
            raise CommandError(e)
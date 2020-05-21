import pandas as pd
import math
import os
import threading
import logging
from .models import City, Province, Community, Country, Language

class InitializingDataInTablesException(Exception):
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR,'./job/static/job/data/csv/')
SUFFIX = ''
COUNTRIES_CSV = f'{CSV_PATH}country{SUFFIX}.csv'
COMMUNITIES_CSV = f'{CSV_PATH}community{SUFFIX}.csv'
PROVINCES_CSV = f'{CSV_PATH}province{SUFFIX}.csv'
CITIES_CSV = f'{CSV_PATH}city{SUFFIX}.csv'

BLANK_COLUMN = 'Unnamed: 0'

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
        print(f'Error: {e}')

def _insert_countries(countries_csv=COUNTRIES_CSV):
    Country.objects.all().delete()
    entries = []
    countries_df = _get_df(countries_csv)
    for e in countries_df.T.to_dict().values():
        entries.append(Country(**e))
    Country.objects.bulk_create(entries)

def _insert_communities(communities_csv = COMMUNITIES_CSV):
    Community.objects.all().delete()
    entries = []
    provinces_df = _get_df(communities_csv)
    for e in provinces_df.T.to_dict().values():
        country_id = e['country_id']
        country = Country.objects.get(id=country_id)
        e['country'] = country
        entries.append(Community(**e))
    Community.objects.bulk_create(entries)

def _insert_provinces(provinces_csv=PROVINCES_CSV):
    Province.objects.all().delete()
    entries = []
    provinces_df = _get_df(provinces_csv)
    spain = Country.objects.filter(name="España")[0]
    for e in provinces_df.T.to_dict().values():
        e['country'] = spain
        entries.append(Province(**e))
    Province.objects.bulk_create(entries)

def _insert_cities(cities_csv=CITIES_CSV):
    City.objects.all().delete()
    entries = []
    cities_df = _get_df(cities_csv)
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

def insert_languages():
    Language.objects.all().delete()
    for l in Language.LANGUAGES:
        for l_ in Language.LEVELS:
            try:
                Language.objects.get_or_create(name=l, level=l_)
            except Exception as e:
                print('Error:')
                print(f"name={l}, level={l_}")
                print(e)

def initialize_database():
    """
    Initialize Language Country, Community, Province, City tables
    """

    def initialization():
        print('Initializing database...')
        logging.info('Initializing database...')
        try:
            if Language.objects.all().count() == 0:
                insert_languages()
            if Province.objects.all().count() == 0:
                print(f'BASE_DIR2: {BASE_DIR}')
                print(f'CSV_PATH2: {CSV_PATH}')
                insert_locations()
        except Exception as e:
            message = 'Have you done the migrations with python manage.py makemigrations and python manage.py migrate?'
            #raise InitializingDataInTablesException(f'{e}. InitializingDataInTablesException: {message}')

    thread = threading.Thread(target=initialization)
    thread.start()


if __name__ != '__main__':
    pass
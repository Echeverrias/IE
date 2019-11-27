import pandas as pd
import math
from .models import Job, City, Province, Community, Country, Language, Company
import sqlite3
import time
from datetime import date

CSV_PATH = 'static/data/csv/'
SUFFIX = '_20191125'
COUNTRIES_CSV = f'{CSV_PATH}country{SUFFIX}.csv'
COMMUNITIES_CSV = f'{CSV_PATH}community{SUFFIX}.csv'
PROVINCES_CSV = f'{CSV_PATH}province{SUFFIX}.csv'
#CITIES_CSV = f'{CSV_PATH}city{SUFFIX}.csv'
#CITIES_CSV = f'{CSV_PATH}cities.csv'
CITIES_CSV = f'{CSV_PATH}cities 06112019.csv'

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
    print(provinces_df)
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



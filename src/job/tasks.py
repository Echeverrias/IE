import pandas as pd
import math
from .models import Job, City, Province, Community, Country, Language
import sqlite3
import time

COUNTRIES_CSV = 'static/data/countries.csv'
COMMUNITIES_CSV = 'static/data/communities.csv'
PROVINCES_CSV = 'static/data/provinces.csv'
CITIES_CSV = 'static/data/cities.csv'

BLANK_COLUMN = 'Unnamed: 0'

def get_df(path):
    df = pd.read_csv(path)
    try:
        df.drop([BLANK_COLUMN], axis=1, inplace=True)
    except:
        pass
    return df

def insert_countries():
    Country.objects.all().delete()
    entries = []
    countries_df = get_df(COUNTRIES_CSV)
    for e in countries_df.T.to_dict().values():
        entries.append(Country(**e))
    Country.objects.bulk_create(entries)

def insert_communities():
    Community.objects.all().delete()
    entries = []
    provinces_df = get_df(COMMUNITIES_CSV)
    for e in provinces_df.T.to_dict().values():
        country_id = e['country']
        country = Country.objects.get(id=country_id)
        e['country'] = country
        entries.append(Community(**e))
    Community.objects.bulk_create(entries)

def insert_provinces():
    Province.objects.all().delete()
    entries = []
    provinces_df = get_df(PROVINCES_CSV)
    for e in provinces_df.T.to_dict().values():
        country_id = e['country']
        country = Country.objects.get(id=country_id)
        e['country'] = country
        entries.append(Province(**e))
    Province.objects.bulk_create(entries)


def insert_cities():
    City.objects.all().delete()
    entries = []
    cities_df = get_df(CITIES_CSV)
    for e in cities_df.T.to_dict().values():
        country_id = e['country']
        province_id = e['province']
        if country_id and (not math.isnan(country_id)):
            try:
                country = Country.objects.get(id=country_id)
                e['country'] = country
            except:
                print(f'Error in country_id:{country_id}')
                continue
        else:
            continue
        if province_id and (not math.isnan(province_id)):
            try:
                province = Province.objects.get(id=province_id)
                e['province'] = province
            except:
                print(f'Error in province_id:{province_id}')
                e['province'] = None
        else:
            e['province'] = None
        entries.append(City(**e))
    City.objects.bulk_create(entries)


def insert_locations():
    insert_countries()
    insert_communities()
    insert_provinces()
    insert_cities()

def delete_locations():
    Country.objects.all().delete()
    Community.objects.all().delete()
    Province.objects.all().delete()
    City.objects.all().delete()

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


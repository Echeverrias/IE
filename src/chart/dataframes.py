import os
import pandas as pd
import geopandas as gpd
from job.models import Job
from django.db.models import Sum, Count, Avg, Q, F, Value
from django.db.models.functions import Concat
from utilities import trace, Lock

from collections import namedtuple

# Creamos el constructor de la 'namedtuple'
Annotation = namedtuple('Annotation', 'new_column operator column')

SPAIN_FILE = 'chart/data/spain.geojson'

def get_job_queryset():
    return Job.objects.all().exclude_first_job().exclude_expirated_offers().annotate_location().annotate_mean_salary()

@trace
def fill_missings_group_by(df, groupby, groupby2, default_value):
    # Añadir areas que faltan en nacionalidades
    df2 = df
    groupby_s = set(df[groupby].unique())
    groupby2_values = list(df[groupby2].unique())
    sets = []
    for value in groupby2_values:
        sets.append(set(df[df[groupby2] == value][groupby].unique()))
    data_columns = set(df.columns) - {groupby, groupby2}
    for i, s in enumerate(sets):
        differences = groupby_s - s
        len_dif = len(differences)
        if differences:
            d = {
                groupby: list(differences),
                groupby2: [groupby2_values[i]] * len_dif
            }
            for dc in data_columns:
                d.update({dc: [default_value] * len_dif})
            df2 = df.append(pd.DataFrame(d), ignore_index=True)  # !Importante: reasignar el dataframe
            df2.sort_values([groupby, groupby2], inplace=True)  # !! Importante
            df2.to_csv('prueba1.csv', index=False) #ñapa
            print(df2)
    return df2


def get_df_from_queryset(queryset, columns=None):
    columns = columns or [field.name for field in type(queryset[0])._meta.fields]
    qs_dict = queryset.values(*columns)
    return pd.DataFrame.from_records(qs_dict)

def get_df_groupby_from_queryset(queryset, group_by_list, operations):
    qs_dict = queryset.values(*group_by_list).order_by(*group_by_list).annotate(**operations)
    df = pd.DataFrame.from_records(qs_dict)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(df)
    df.to_csv('filter_df.csv', index=False)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    if len(group_by_list) > 1:
        df = fill_missings_group_by(df, group_by_list[0], group_by_list[1], 0)
    print('******************************************************************************************')
    print(df)
    print('******************************************************************************************')
    #df = df.set_index(group_by)
    #df.sort_index(inplace=True, ascending=False)
    return df


def get_filtered_jobs_by_nationality(show_national_areas, show_international_areas):
    if not show_national_areas:
        qs = get_job_queryset().internationals()
    elif not show_international_areas:
        qs = get_job_queryset().nationals()
    else:
        qs = get_job_queryset()
    return qs

@Lock()
@trace
def get_annotations_job_in_groupby_df(national_filter, international_filter, groupby_list, aggregations):
    print('-----------------------------------------------------------------------')
    print('get_annotations_job_in_groupby_df')
    qs = get_filtered_jobs_by_nationality(national_filter, international_filter)
    print('qs', qs[0:2])
    #operations = { a.new_column: a.operator(a.column) for a in annotations}
    print('operations', aggregations)
    #columns = [groupby, *[a.column for a in annotations]]
    #print('columns:', columns)
    #qs = qs.values(*columns)
    print('qs.values', qs[0:2])
    df = get_df_groupby_from_queryset(qs, groupby_list, aggregations)
    print('df')
    print(df.head(3))
    df.to_csv('df_clean.csv')
    return df

def get_salaries_per_area_df(national_filter=True, international_filter=True):
    annotations = [Annotation('mean_salaries', Avg, 'mean_salary')]
    aggregations = {'mean_salaries': Avg('mean_salary')}
    if (national_filter & international_filter):
        groupby = ['area', 'nationality']
    else:
        groupby = ['area']
    return get_annotations_job_in_groupby_df(national_filter, international_filter, groupby, aggregations)

def get_companies_with_more_vacancies_df(national_filter=True, international_filter=True):
    annotations = [Annotation('mean_salaries', Avg, 'mean_salary')]
    aggregations = {
        'vacancies': Sum('vacancies'),
        'name': Concat(F('company'), Value(' ('), F('company__company_category'), Value(')')),
    }
    if (national_filter & international_filter):
        groupby = ['company', 'nationality']
    else:
        groupby = ['company']
    return get_annotations_job_in_groupby_df(national_filter, international_filter, groupby, aggregations)

def get_vacancies_and_registered_people_per_area_df(national_filter=True, international_filter=True):
    annotations = [Annotation('vacancies', Sum, 'vacancies')]
    aggregations = {'vacancies': Sum('vacancies'), 'registered_people': Sum('registered_people')}
    return get_annotations_job_in_groupby_df(national_filter, international_filter, ['area'], aggregations)

def get_vacancies_per_area_df(national_filter=True, international_filter=True):
    annotations = [Annotation('vacancies', Sum, 'vacancies')]
    aggregations = {'vacancies': Sum('vacancies')}
    if (national_filter & international_filter):
        groupby = ['area', 'nationality']
    else:
        groupby = ['area']
    return get_annotations_job_in_groupby_df(national_filter, international_filter, groupby, aggregations)

def get_registered_people_per_area_df(national_filter=True, international_filter=True):
    annotations = [Annotation('registered_people', Sum, 'registered_people')]
    aggregations = {'registered_people': Sum('registered_people')}
    if (national_filter & international_filter):
        groupby = ['area', 'nationality']
    else:
        groupby = ['area']
    return get_annotations_job_in_groupby_df(national_filter, international_filter, groupby, aggregations)

"""
def get_national_and_international_vacancies_per_area_df():
    annotations = [Annotation('vacancies', Sum, 'vacancies')]
    aggregations = {'vacancies': Sum('vacancies')}
    return get_annotations_job_in_groupby_df(True, True, ['area', 'nationality'], aggregations)

def get_national_and_international_registered_people_per_area_df():
    annotations = [Annotation('registered_people', Sum, 'registered_people')]
    aggregations = {'registered_people': Sum('registered_people')}
    return get_annotations_job_in_groupby_df(True,True, ['area', 'nationality'], aggregations)
"""
def get_vacancies_per_province_df():
    annotations = [Annotation('vacancies', Sum, 'vacancies')]
    aggregations = {'vacancies': Sum('vacancies')}
    df = get_annotations_job_in_groupby_df(True, False, ['province_name'], aggregations)
    df.rename(columns={'province_name': 'province'}, inplace=True)
    return df

def get_registered_people_per_province_df():
    annotations = [Annotation('registered_people', Sum, 'registered_people')]
    aggregations = {'registered_people': Sum('registered_people')}
    df = get_annotations_job_in_groupby_df(True, False, ['province_name'], aggregations)
    df.rename(columns={'province_name': 'province'}, inplace=True)
    return df

def get_salary_per_province_df():
    annotations = [Annotation('mean_salaries', Avg, 'mean_salary')]
    aggregations = {'mean_salaries': Avg('mean_salary')}
    df = get_annotations_job_in_groupby_df(True, False, ['province_name'], aggregations)
    df.rename(columns={'province_name': 'province'}, inplace=True)
    return df


def get_spain_gdf():
    return gpd.read_file(SPAIN_FILE)

def merge_spain_with(df, mergeby_province_or_community):
    spain_gpd = get_spain_gdf()
    print(spain_gpd.columns)
    print(df.columns)
    #new_gpd = spain_gpd.merge(spain_gpd, df, on=mergeby_province_or_community)
    new_gpd = spain_gpd.merge(df, on=mergeby_province_or_community)
    return new_gpd


def get_vacancies_per_province_gdf():
    df = get_vacancies_per_province_df()
    print(df.columns)
    return merge_spain_with(df, 'province')

def get_registered_people_per_province_gdf():
    df = get_registered_people_per_province_df()
    print(df.columns)
    return merge_spain_with(df, 'province')

def get_salary_per_province_gdf():
    df = get_salary_per_province_df()
    print(df.columns)
    return merge_spain_with(df, 'province')


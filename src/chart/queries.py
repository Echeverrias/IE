from job.models import Job, Community, Province, City
import os
import pandas as pd
import geopandas as gpd
from django.db.models import Q
from datetime import date

QUERIES_DIR = os.path.dirname(os.path.abspath(__file__))

JOB_COLUMNS = ['vacancies', 'registered_people', 'area', 'category_level', 'working_day']

JOBS_QS = Job.objects.all()
PROVINCES_QS = Province.objects.all()
COMMUNITIES_QS = Community.objects.all()

GRAPHICS = {}

EXPIRATION_DATE_Q = Q(expiration_date__lt=date.today())
FIRST_JOB_Q = Q(type=Job.TYPE_FIRST_JOB)
COUNTRY_SPAIN_Q =  Q(country__name="España")
SPAIN_FILE = 'chart/data/spain.geojson'


#
def get_spain_gdf():
    return gpd.read_file(SPAIN_FILE)

#
def merge_spain_with(df, mergeby_province_or_community):
    spain_gpd = get_spain_gdf()
    print(spain_gpd.columns)
    print(df.columns)
    #new_gpd = spain_gpd.merge(spain_gpd, df, on=mergeby_province_or_community)
    new_gpd = spain_gpd.merge(df, on=mergeby_province_or_community)
    return new_gpd

#
def get_df_from_queryset(queryset, columns=None, queries_dict=None):
    qs = queryset
    if queries_dict:
        filter = queries_dict.get('filter', None)
        if filter:
            for q in filter:
                qs = qs.filter(q)
        exclude = queries_dict.get('exclude', None)
        if exclude:
            for q in exclude:
                qs = qs.exclude(q)
    columns = columns or [field.name for field in type(qs[0])._meta.fields]
    tuples = qs.values_list(*columns)
    return pd.DataFrame.from_records(list(tuples), columns=columns)

##
def  get_job_df_with_communities_and_provinces(queries=None, columns=None):
    c_df = get_df_from_queryset(COMMUNITIES_QS, ['id', 'name'])
    p_df = get_df_from_queryset(PROVINCES_QS, ['id', 'name', 'community'])
    j_df = get_df_from_queryset(JOBS_QS, queries_dict=queries)
    j_df = j_df.dropna(subset=['province'])
    # provinces + communities
    p_df = pd.merge(p_df, c_df, left_on='community', right_on='id')
    p_df.drop(['community', 'id_y'], axis=1, inplace=True)
    p_df.rename(columns={'name_x': 'province_name', 'name_y': 'community', 'id_x': 'id_province'}, inplace=True)
    # job + (province - communities)
    try:
        j_df.drop('province_name', axis=1, inplace=True)
    except Exception:
        pass
    j_df = pd.merge(j_df, p_df, left_on='province', right_on='id_province')
    j_df.drop(['province', 'id_province'], axis=1, inplace=True)
    j_df.rename(columns={'province_name': 'province'}, inplace=True)
    """
    column_destiny_index = j_df.columns.get_loc('province_name')
    column_origin_index = j_df.columns.get_loc('cities')
    for i in j_df.index:
        cities_qs = j_df.iat[i, column_origin_index]
        if cities_qs:
            province_name = cities_qs.all()[0].province.name
            j_df.iat[i, column_destiny_index] = province_name
    """

    if columns:
        j_df = j_df[columns]

    return j_df

def get_columns_from_model(model_type):
    models = {
        'Job': [field['name'] for field in Job._meta.fields],
        'Community': [field['name'] for field in Community._meta.fields],
        'City': [field['name'] for field in City._meta.fields],
        'Province': [field['name'] for field in Province._meta.fields],
    }
    if type(model_type) == str:
        model = model_type
    else:
        model = type(model_type).__name__
    return models.get(model, [])

#
def get_df_groupby(df, index, operation_columns, operation):
    print('grouby')
    print(index, operation_columns)
    print(df.columns)
    print(df.head(2))
    df2 = df.set_index(index)
    print(df2.columns)
    print(df2.head(2))
    # df2 = df.groupby(['area']).sum()
    try:
        operation_columns.remove(index)
    except:
        pass
    df2 = df2.groupby([index])[operation_columns].agg(operation)
    print('OK')
    df2.sort_index(inplace=True, ascending=False)
    #df2.sort_values(by=operation_column, ascending=False, inplace=True)
    return df2




def get_salaries_per_areas_df(show_national_areas=True, show_international_areas=True):
    exclude_queries = []
    if not show_national_areas:
        exclude_queries.append(COUNTRY_SPAIN_Q)
    elif not show_international_areas:
        exclude_queries.append(~COUNTRY_SPAIN_Q)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    query = (Q(minimum_salary=0) & Q(maximum_salary=0))
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    exclude_queries.append(query)
    queries = {
        'exclude': exclude_queries,
    }
    j_qs = JOBS_QS
    columns = ['minimum_salary', 'maximum_salary', 'area']
    df = get_df_from_queryset(j_qs, columns, queries)
    print(df.columns)
    print(df.head(2))
    df['count'] = 1
    columns.pop()
    columns.append('count')
    df = get_df_groupby(df, 'area', columns, 'sum')
    print(df.columns)
    print(df.head(2))
    df['mean'] = 0.0
    print('--------------------------------------------------')
    print(df.columns)
    print('--------------------------------------------------')
    i_min_salary = df.columns.get_loc('minimum_salary')
    i_max_salary = df.columns.get_loc('maximum_salary')
    i_count = df.columns.get_loc('count')
    i_mean = df.columns.get_loc('mean')
    for i in range(0, df.shape[0]):
        min_salary = df.iat[i, i_min_salary]
        max_salary = df.iat[i, i_max_salary]
        count = df.iat[i, i_count]
        value = (min_salary/count + max_salary/count)/2
        df.iat[i, i_mean] = value
    return df.drop(columns, axis=1)

def _get_vacancies_or_registered_people_per_area_or_province_df(groupby, column, show_national_vacancies=True, show_international_vacancies=True):
    print('_get_vacancies_or_registered_people_per_area_or_province_df') #%
    print(groupby, column)
    exclude_queries = []
    if not show_national_vacancies:
        exclude_queries.append(COUNTRY_SPAIN_Q)
    elif not show_international_vacancies:
        exclude_queries.append(~COUNTRY_SPAIN_Q)
    exclude_queries.append(EXPIRATION_DATE_Q)
    exclude_queries.append(FIRST_JOB_Q)
    queries = {
        'exclude': exclude_queries,
    }
    columns = [column, groupby]
    if groupby == 'area':
        j_qs = JOBS_QS
        df = get_df_from_queryset(j_qs, columns, queries)
        print('as')
        print(df.head(2))
        print(df.columns)
        print('as')
    elif groupby == 'province':
        #columns.append('community')
        df = get_job_df_with_communities_and_provinces(queries)

        print('b1')#%
    columns.pop()
    return get_df_groupby(df, groupby, columns, 'sum')


def get_vacancies_per_province_df():
    return _get_vacancies_or_registered_people_per_area_or_province_df('province','vacancies', True, False)

def get_registered_people_per_province_df():
    return _get_vacancies_or_registered_people_per_area_or_province_df('province','registered_people', True, False)

def get_vacancies_per_areas_df(show_national_vacancies=True, show_international_vacancies=True):
    return _get_vacancies_or_registered_people_per_area_or_province_df('area', 'vacancies', show_national_vacancies, show_international_vacancies)

def get_registered_people_per_areas_df(show_national_vacancies=True, show_international_vacancies=True):
    return _get_vacancies_or_registered_people_per_area_or_province_df('area', 'registered_people', show_national_vacancies, show_international_vacancies)

def _get_vacancies_or_registered_people_per_province_gdf(vacancies_or_registered_people):
    if vacancies_or_registered_people == 'vacancies':
        df = get_vacancies_per_province_df()
    else:
        df = get_registered_people_per_province_df()
    return merge_spain_with(df, 'province')

def get_vacancies_per_province_gdf():
    return _get_vacancies_or_registered_people_per_province_gdf('vacancies')

def get_registered_people_per_province_gdf():
    return _get_vacancies_or_registered_people_per_province_gdf('registered_people')
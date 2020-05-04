import os
import pandas as pd
import geopandas as gpd
from job.models import Job
from django.db.models import Sum, Count, Avg, Q, F, Value, Func
from django.db.models.functions import Concat
from utilities.utilities import trace, Lock
from collections import namedtuple
from datetime import date
# Creamos el constructor de la 'namedtuple'
Annotation = namedtuple('Annotation', 'new_column operator column')

SPAIN_FILE = 'chart/data/spain.geojson'


def _get_fields_from_queryset(qs):
    try:
        return [field.name for field in type(qs[0])._meta.fields]
    except:
        return []

def _get_initial_job_queryset(qs, desc=None):
    dinitial_qs = {
        "available_offers": lambda qs : qs.exclude_first_job().exclude_expirated_offers().annotate_location(),
        "in_provinces": lambda qs : qs.exclude(province=None).annotate(province_aux=F('province__name')),
        "in_companies": lambda qs : qs.exclude(company=None).annotate(company_aux=Concat(F('company__name'), Value(' ('), F('company__category'), Value(')'))),
        "get_mean_salary": lambda qs : qs.annotate_mean_salary(),
        "offers_historical": lambda qs: qs.annotate(first_publication_date_aux=Func(F('first_publication_date'), function='MONTH'))
    }
    return dinitial_qs.get(desc, lambda *args: qs)(qs)

def get_initial_queryset(model, desc=None):
    dinitial_qs = {
        "job": lambda qs, desc :_get_initial_job_queryset(qs or Job.objects.all(), desc)
    }
    qs = None
    for desc_ in desc.split('__'):
        qs = dinitial_qs.get(model, lambda *args :qs)(qs, desc_)
    return qs


def _get_filtered_job_queryset(filter_description, **kwargs):
    qs = kwargs.get('qs')
    year = kwargs.get('year')
    if not qs:
        qs = _get_initial_job_queryset()
    if not year:
        year = date.today().year
    qs_d = {
        'exclude-nationality-nacional': lambda *args : args[0].internationals(),
        'filter-nationality-internacional': lambda *args: args[0].internationals(),
        'exclude-nationality-internacional': lambda *args : args[0].nationals(),
        'filter-nationality-nacional': lambda *args : args[0].nationals(),
        'filter-available-jobs-in-year': lambda *args: args[0].availables_in_year(args[1]),
        'filter-first_publication_date-in_range': lambda *args: args[0].first_publication_date_in_year_range(*_years_ago_range()),
        'filter-first_publication_date-in_range_': lambda *args: args[0]._first_publication_date_in_month_range_(*_months_ago_range_()),
        'i-filter-available-jobs-in-years-ago': lambda *args: gen_historical_available_jobs(args[1],args[0]),
        'i-filter-publication-date-jobs-in-years-ago': lambda *args: gen_historical_first_publication_date_jobs(args[1],args[0]),
    }
    return qs_d.get(filter_description, lambda *args :None)(qs, year)


def _get_filtered_queryset(model, filter_description, **kwargs):
    print(f'_get_filtered_queryset({model}, {filter_description}, {kwargs})')
    qs = kwargs.get('qs')
    year = kwargs.get('year')
    print(f'qs: {qs}')
    print(f'year: {year}')
    dmodel = {
        'job': lambda filter_description, **kwargs : _get_filtered_job_queryset(filter_description, **kwargs),
    }
    return dmodel.get(model, lambda fd, **kwargs :None)(filter_description, qs=qs, year=year)


def _get_operation(operator, aggregation):
    operator_aggregation = operator + "-" + aggregation
    doperation = {
        'avg-mean_salary': {'mean_salary': Avg('mean_salary')},
        'sum-vacancies': {'vacancies': Sum('vacancies')},
        'sum-registered_people': {'registered_people': Sum('registered_people')},
        'concat-company-category': {'name': Concat(F('company'), Value(' ('), F('company__category'), Value(')'))},
    }
    return  doperation.get(operator_aggregation, None)

def _get_operations(operators, aggregations):
    zipped = zip(operators, aggregations)
    print(f'zipped: {zipped}')
    operations = {}
    for o, a in zipped:
        operation = _get_operation(o, a)
        operations.update(operation)
    return operations

def _years_ago_range(n_years_ago=3) -> tuple:
    actual_year = date.today().year
    init_year = actual_year - n_years_ago
    end_year = actual_year
    earliest_job = Job.objects.earliest('created_at')
    earliest_job_year = earliest_job.created_at.year
    start_year = init_year if (earliest_job_year <= init_year) else earliest_job_year
    return (start_year, end_year + 1)

def _months_ago_range_(n_months_ago=3) -> tuple:
    actual_month = 12
    init_month = actual_month - n_months_ago
    end_month = actual_month
    earliest_job = Job.objects.earliest('created_at')
    earliest_job_month = earliest_job.created_at.month
    start_month = init_month if (earliest_job_month <= init_month) else earliest_job_month
    return (start_month, end_month + 1)

def gen_historical_available_jobs(n_years_ago=3, qs=None):
    if not qs:
        qs = Job.objects.all()
    for i in _years_ago_range(n_years_ago):
        yield qs.availables_in_year(i)

def gen_historical_first_publication_date_jobs(n_years_ago=3, qs=None):
    if not qs:
        qs = Job.objects.all()
    for i in _years_ago_range(n_years_ago):
        yield qs.first_publication_date_in_year(i)

def get_df_from_queryset(queryset, columns=None):
    columns = columns or _get_fields_from_queryset(queryset)
    qs_dict = queryset.values(*columns)
    return pd.DataFrame.from_records(qs_dict)

def _fill_missings_group_by(df, groupby, groupby2, default_value):
    # Añadir combinaciones que faltan
    print();print();print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('fill_missings_group')
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(f'header: {df.head(1)}')

    df2 = df
    groupby_values_s = set(df[groupby].unique())
    groupby2_values = list(df[groupby2].unique())
    groupby2_values.sort()
    print(f'groupby2: {groupby2}')
    print(f'groupby2_values: {groupby2_values}')
    groupby_values_s_for_groupby2_value_l = []
    for value in groupby2_values:
        groupby_values_s_for_groupby2_value_l.append(set(df[df[groupby2] == value][groupby].unique()))
    data_columns = set(df.columns) - {groupby, groupby2}
    for i, values_s in enumerate(groupby_values_s_for_groupby2_value_l):
        differences = groupby_values_s - values_s
        len_dif = len(differences)
        if differences:
            d = {
                groupby: list(differences),
                groupby2: [groupby2_values[i]] * len_dif
            }
            for dc in data_columns:
                d.update({dc: [default_value] * len_dif})
            df2 = df2.append(pd.DataFrame(d), ignore_index=True)  # !Importante: reasignar el dataframe
            print();print('---------')
            print(f'differences: {differences}')
            print(f'groupby2_values[i]: {groupby2_values[i]}')
            print('---------');print();


    df2.sort_values([groupby, groupby2], inplace=True)  # !! Importante
    df2.to_csv('prueba1.csv', index=False) #ñapa
    print(df2);print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&%%%%');print();
    return df2

def _get_df_groupby_from_queryset(queryset, lgroupby:list, loperator:list, laggregation:list):
    print(f'queryset: {queryset}')
    print(f'lgroupby: {lgroupby}')
    print(f'loperator: {loperator}')
    print(f'laggregation: {laggregation}')
    doperations = _get_operations(loperator, laggregation)

    # Prepare the name of the new columns that refers an existing columns
    SPECIAL_COLS = ['province', 'company', 'first_publication_date']
    SUFFIX = '_aux'
    lgroupby_ = [i + SUFFIX if i in SPECIAL_COLS else i for i in lgroupby]
    print(f'lgroupby_: {lgroupby_}')
    dqs = queryset.values(*lgroupby_).order_by(*lgroupby_).annotate(**doperations)
    df = pd.DataFrame.from_records(dqs)
    print();print();print('<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>')
    print(df.head(3));print()

    # The original columns will be removed and replaced  with the new ones
    for col in lgroupby_:
        clean_col = col.replace(SUFFIX, "")
        if clean_col in SPECIAL_COLS:
            df.rename(columns={col: clean_col}, inplace=True)
    print(df.head(3));
    print()
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(df)
    df.to_csv('filter_df.csv', index=False)
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    if len(lgroupby) > 1:
        df = _fill_missings_group_by(df, lgroupby[0], lgroupby[1], 0)
    print('******************************************************************************************')
    print(df)
    print('******************************************************************************************')
    #df = df.set_index(group_by)
    #df.sort_index(inplace=True, ascending=False)
    return df

def get_spain_gdf():
    return gpd.read_file(SPAIN_FILE)

def merge_spain_gdf_with_df(df, mergeby_province_or_community):
    print();print();print('merge_spain_gdf_with_df')
    spain_gpd = get_spain_gdf()
    print(spain_gpd.columns)
    print('SPAIN')
    print(spain_gpd['province'])
    print();print('DF');print(df['province'])
    #new_gpd = spain_gpd.merge(spain_gpd, df, on=mergeby_province_or_community)
    new_gpd = spain_gpd.merge(df, on=mergeby_province_or_community)
    return new_gpd


def get_df(model, desc, **kwargs):
    lq = kwargs.get('q', [])
    lgroupby = kwargs.get('groupby', [])
    loperator = kwargs.get('operator', [])
    laggregation = kwargs.get('aggregation', [])
    qs = get_initial_queryset(model, desc)
    print();print(f'get_df - qs: {qs}')
    for q in lq:
        qs =_get_filtered_queryset(model, q, qs=qs)
    print(f'get_df - qs: {qs}')
    df = _get_df_groupby_from_queryset(qs, lgroupby, loperator, laggregation)
    if lgroupby == 'province':
        df.rename(columns={'province_name': 'province'}, inplace=True)
        return merge_spain_gdf_with_df(df, 'province')
    return df


##################################################################################################################
###################################################################################################################

"""

@trace
def fill_missings_group_by_(df, groupby, groupby2, default_value):
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


def get_df_from_queryset_(queryset, columns=None):
    columns = columns or _get_fields_from_queryset(queryset)
    qs_dict = queryset.values(*columns)
    return pd.DataFrame.from_records(qs_dict)

def get_df_groupby_from_queryset_(queryset, group_by_list, operations):
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
        qs = _get_initial_job_queryset().internationals()
    elif not show_international_areas:
        qs = _get_initial_job_queryset().nationals()
    else:
        qs = _get_initial_job_queryset()
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
    df = get_df_groupby_from_queryset_(qs, groupby_list, aggregations)
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

def get_national_and_international_vacancies_per_area_df():
    annotations = [Annotation('vacancies', Sum, 'vacancies')]
    aggregations = {'vacancies': Sum('vacancies')}
    return get_annotations_job_in_groupby_df(True, True, ['area', 'nationality'], aggregations)

def get_national_and_international_registered_people_per_area_df():
    annotations = [Annotation('registered_people', Sum, 'registered_people')]
    aggregations = {'registered_people': Sum('registered_people')}
    return get_annotations_job_in_groupby_df(True,True, ['area', 'nationality'], aggregations)

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




def get_registered_people_per_province_gdf():
    df = get_registered_people_per_province_df()
    print(df.columns)
    return merge_spain_with(df, 'province')

def get_salary_per_province_gdf():
    df = get_salary_per_province_df()
    df.rename(columns={'province_name': 'province'}, inplace=True)
    return merge_spain_with(df, 'province')
    
def get_vacancies_per_province_gdf():
    df = get_vacancies_per_province_df()
    df.rename(columns={'province_name': 'province'}, inplace=True)
    return merge_spain_with(df, 'province')
"""
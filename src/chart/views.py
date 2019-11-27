from django.http import HttpResponse
from django.shortcuts import render
from utilities import trace
from .dataframes import (
    get_vacancies_per_area_df,
    get_registered_people_per_area_df,
    get_vacancies_and_registered_people_per_area_df,
    get_salaries_per_area_df,
    get_vacancies_per_province_gdf,
    get_registered_people_per_province_gdf,
    get_salary_per_province_gdf,
    get_companies_with_more_vacancies_df,

)
from .figures import (
    get_buffer_of_plot,
    get_spain_map_buffer,
    save_figure_as_image,

)
import os
import threading
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_images_dir():
    return os.path.join(f'static/img/chart/{date.today().month}')


def _get_response_from_buffer_value(buffer_value, content_type):
    response = HttpResponse(buffer_value, content_type=content_type)
    response['Content-Length'] = str(len(response.content))
    return response


@trace
def _get_vacancies_or_registered_people_per_area_buffer(vacancies_or_registered_people, show_national_vacancies=True, show_international_vacancies=True):
    if vacancies_or_registered_people == 'vacancies':
        df = get_vacancies_per_area_df(show_national_vacancies, show_international_vacancies)
        print('a1', df.columns) #%
        sub = "Vacantes"
    else:
        df = get_registered_people_per_area_df(show_national_vacancies, show_international_vacancies)
        sub = "Gente registrada"
    data = []
    legend = None
    if show_national_vacancies and show_international_vacancies:
        title = f'{sub} por área'
        legend=(['nacional', 'internacional'], 'upper right')
        data.append(df.loc[df['nationality']=='nacional', vacancies_or_registered_people])
        data.append(df.loc[df['nationality']=='internacional', vacancies_or_registered_people])
    elif show_national_vacancies:
        title = f'{sub} por área en España'
        data.append(df[vacancies_or_registered_people])
    else:
        title = f'{sub} por área en el extranjero'
        data.append(df[vacancies_or_registered_people])

    buffer_value = get_buffer_of_plot(df['area'].unique(), data, 'Áreas', sub, title, legend, True, ('area', df['area'].unique()))
    return buffer_value


def vacancies_or_registered_people_per_area_view(request, column, type_):
    print('vacancies_or_registered_people_per_area_view')
    print(f'column: {column}')
    print(f'type_: {type_}')
    show_national_vacancies = False
    show_international_vacancies = False
    if type_ == 'national':
        show_national_vacancies = True
    elif type_ == 'international':
        show_international_vacancies = True
    buffer_value = _get_vacancies_or_registered_people_per_area_buffer(column, show_national_vacancies, show_international_vacancies)
    return _get_response_from_buffer_value(buffer_value, 'image/png')

"""
def _get_national_and_international_vacancies_or_registered_people_per_area_buffer(vacancies_or_registered_people):
    if vacancies_or_registered_people == 'vacancies':
        df = get_national_and_international_vacancies_per_area_df()
        print('a1', df.columns) #%
        sub = "Vacantes"
    else:
        df = get_national_and_international_registered_people_per_area_df()
        sub = "Gente registrada"
    title = f'{sub} por área'
    legend=(['nacional', 'internacional'], 'upper right' )
    c1 = df.loc[df['nationality']=='nacional', vacancies_or_registered_people]
    c2 = df.loc[df['nationality']=='internacional', vacancies_or_registered_people]
    buffer_value = get_buffer_of_plot(df['area'].unique(), [c1,c2], 'Áreas', sub, title, legend, True)
    return buffer_value
"""

def national_and_international_vacancies_or_registered_people_per_area_view(request, column):
    print('vacancies_or_registered_people_per_area_view')
    buffer_value = _get_vacancies_or_registered_people_per_area_buffer(column)
    return _get_response_from_buffer_value(buffer_value, 'image/png')


@trace
def _get_vacancies_and_registered_people_per_area_buffer(national_filter=True, international_filter=True):
    df = get_vacancies_and_registered_people_per_area_df(national_filter, international_filter)
    legend = (['Vacantes', 'Gente registrada'], 'upper rigth')
    if not international_filter:
        sub = " en España"
    elif not national_filter:
        sub = " en el extranjero"
    title = f'Vacantes y gente registrada {sub}'
    df.to_csv('df_clean.csv') #ñapa
    buffer_value = get_buffer_of_plot(df['area'].unique(), [df['vacancies'], df['registered_people']], 'Áreas', 'Nº', title, legend, True)
    return buffer_value

def vacancies_and_registered_people_per_area_view(request, type_):
    show_national_vacancies = False
    show_international_vacancies = False
    if type_ == 'national':
        show_national_vacancies = True
    elif type_ == 'international':
        show_international_vacancies = True
    buffer_value = _get_vacancies_and_registered_people_per_area_buffer(show_national_vacancies, show_international_vacancies)
    return _get_response_from_buffer_value(buffer_value, 'image/png')


def _get_salaries_per_area_buffer(show_national_areas=True, show_international_areas=True):
    df = get_salaries_per_area_df(show_national_areas, show_international_areas)
    print(df) #%
    data = []
    legend = None
    if not show_international_areas:
        title = "Salario nacional bruto anual medio"
        data.append(df['mean_salaries'])
    elif not show_national_areas:
        title = "Salario internacional bruto anual medio"
        data.append(df['mean_salaries'])
    else:
        title = "Salario bruto anual medio"
        data.append(df.loc[df['nationality']=='nacional', 'mean_salaries'])
        data.append(df.loc[df['nationality']=='internacional', 'mean_salaries'])
        legend = (['nacional', 'internacional'], 'upper right')
    buffer_value = get_buffer_of_plot(df['area'].unique(), data, 'Áreas', '€', title, legend, True, ('area', df['area'].unique()))
    return buffer_value

def salaries_per_area_view(request, type_):
    show_national_vacancies = False
    show_international_vacancies = False
    if type_ == 'national':
        show_national_vacancies = True
    elif type_ == 'international':
        show_international_vacancies = True
    buffer_value = _get_salaries_per_area_buffer(show_national_vacancies, show_international_vacancies)
    return _get_response_from_buffer_value(buffer_value, 'image/png')


def _get_companies_with_more_vacancies_buffer(show_national_areas=True, show_international_areas=True):
    df = get_companies_with_more_vacancies_df(show_national_areas, show_international_areas)
    df = df.sort_values('vacancies', ascending=False)[0:15]
    print(df) #%
    data = []
    legend = None
    if not show_international_areas:
        title = "Compañías nacionales"
        data.append(df['vacancies'])
    elif not show_national_areas:
        title = "Compañías internacional"
        data.append(df['vacancies'])
    else:
        title = "Compañías que ofrecen más vacantes"
        data.append(df.loc[df['nationality']=='nacional', 'vacancies'])
        data.append(df.loc[df['nationality']=='internacional', 'vacancies'])
        legend = (['nacional', 'internacional'], 'upper right')
    buffer_value = get_buffer_of_plot(df['name'].unique(), data, 'Compañías', 'Vacantes', title, legend, True, ('name', df['name'].unique()))
    return buffer_value


def companies_with_more_vacancies_view(request, type_):
    show_national_vacancies = False
    show_international_vacancies = False
    if type_ == 'national':
        show_national_vacancies = True
    elif type_ == 'international':
        show_international_vacancies = True
    buffer_value = _get_companies_with_more_vacancies_buffer(show_national_vacancies, show_international_vacancies)
    return _get_response_from_buffer_value(buffer_value, 'image/png')



def national_and_international_salaries_per_area_view(request):
    buffer_value = _get_salaries_per_area_buffer(True, True)
    return _get_response_from_buffer_value(buffer_value, 'image/png')


def _get_vacancies_or_registered_people_per_province_buffer(vacancies_or_registered_people):

    if vacancies_or_registered_people == 'vacancies':
        gdf = get_vacancies_per_province_gdf()
        sub = "Vacantes"
    else:
        gdf = get_registered_people_per_province_gdf()
        sub = "Gente registrada"
    title = f'{sub} por provincias'

    #image_base64 = get_image_base64_from_figure(figure)
   # return image_base64
    buffer_value = get_spain_map_buffer(gdf, vacancies_or_registered_people, title)
    return buffer_value


def _get_salaries_per_province_buffer():
    gdf = get_salary_per_province_gdf()
    buffer_value = get_spain_map_buffer(gdf, 'mean_salaries', "Salario bruto anual")
    return buffer_value

def vacancies_or_registered_people_per_province_view(request, column):
    print('vacancies_or_registered_people_per_province_view')
    print(f'column: {column}')
    buffer_value = _get_vacancies_or_registered_people_per_province_buffer(column)
    return _get_response_from_buffer_value(buffer_value, 'image/png')


def salaries_per_province_view(request):
    buffer_value = _get_salaries_per_province_buffer()
    return _get_response_from_buffer_value(buffer_value, 'image/png')


def main_view(request):
    print('main_view')
    template_name = 'chart/main.html'
    context = None
    print(f'request.GET: {request.GET}')
    try:
        charts_type = request.GET['charts_type']
        context = {
            'charts_type': charts_type,
            'month': date.today().month,
            'url': "img/chart/10/national_salaries_per_area.png"
        }
    except Exception as e:
        pass

   # return HttpResponse('<img src="/chart/one_example/" width="600px" />')
    return render(request, template_name, context)
    # return response


if __name__ != '__main__':

    print('queries - pre_load')
    def _preloading():
        _get_salaries_per_area_buffer(True, False)
        _get_salaries_per_area_buffer(False, True)
        _get_vacancies_or_registered_people_per_area_buffer('vacancies', True, False)
        _get_vacancies_or_registered_people_per_area_buffer('registered_people', True, False)
        _get_vacancies_or_registered_people_per_area_buffer('registered_people', False, True)
        _get_vacancies_or_registered_people_per_area_buffer('vacancies', False, True)
        _get_vacancies_or_registered_people_per_province_buffer('vacancies')
        _get_vacancies_or_registered_people_per_province_buffer('registered_people')

    def execute_preloading():
        images_path = os.path.join(os.path.dirname(_get_images_dir()), str(date.today().month))
        if not os.path.exists(images_path):
            thread = threading.Thread(target=_preloading)
            thread.start()

    #execute_preloading()
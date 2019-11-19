from django.http import HttpResponse
from django.shortcuts import render
from .queries import (
    get_vacancies_per_areas_df,
    get_registered_people_per_areas_df,
    get_salaries_per_areas_df,
    get_vacancies_per_province_gdf,
    get_registered_people_per_province_gdf,

)
from .figures import get_bar_figure, get_spain_map_figure, get_buffer_value_from_figure, save_figure_as_image
import os
import threading
import threading
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



def _get_images_dir():
    return os.path.join(f'static/img/chart/{date.today().month}')


def _get_response_from_buffer_value(buffer_value, content_type):
    response = HttpResponse(buffer_value, content_type=content_type)
    response['Content-Length'] = str(len(response.content))
    return response

def _get_salaries_per_area_buffer(show_national_areas=True, show_international_areas=True):
    df = get_salaries_per_areas_df(show_national_areas, show_international_areas)
    print(df) #%
    title = "Salario bruto anual medio"
    figure = get_bar_figure(df.index, df['mean_salaries'], '€', 'Áreas', title, True, ('area', df.index))
    # image_base64 = get_image_base64_from_figure(figure)
    # return image_base64
    if show_national_areas and not show_international_areas:
        location='national'
    elif show_national_areas and show_international_areas:
        location = 'national and international'
    else:
        location = 'international'
    img_name = f'{location}_salaries_per_area'
    save_figure_as_image(figure, img_name, _get_images_dir())
    buffer_value = get_buffer_value_from_figure(figure)
    return buffer_value


def _get_vacancies_or_registered_people_per_area_buffer(vacancies_or_registered_people, show_national_vacancies=True, show_international_vacancies=True):
    if vacancies_or_registered_people == 'vacancies':
        df = get_vacancies_per_areas_df(show_national_vacancies, show_international_vacancies)
        print('a1', df.columns) #%
        sub = "Vacantes"
    else:
        df = get_registered_people_per_areas_df(show_national_vacancies, show_international_vacancies)
        sub = "Gente registrada"
    if show_national_vacancies and not show_international_vacancies:
        title = f'{sub} por área en España'
        location='national'
    elif show_national_vacancies and show_international_vacancies:
        title = f'{sub} por área en el mundo'
        location = 'national and international'
    else:
        title = f'{sub} por área en el extranjero'
        location = 'international'
    figure = get_bar_figure(df.index, df[vacancies_or_registered_people],sub, 'Áreas', title, True, ('area', df.index))
    #image_base64 = get_image_base64_from_figure(figure)
    #return image_base64
    img_name = f'{location}_{vacancies_or_registered_people}_per_area'
    save_figure_as_image(figure, img_name, _get_images_dir())
    buffer_value = get_buffer_value_from_figure(figure)
    return buffer_value
"""
def _get_vacancies_per_area_buffer(show_national_vacancies=True, show_international_vacancies=True):
    return _get_vacancies_or_registered_people_per_area_buffer('vacancies', show_national_vacancies, show_international_vacancies)

def _get_registered_people_per_area_buffer(show_national_vacancies=True, show_international_vacancies=True):
    return _get_vacancies_or_registered_people_per_area_buffer('registered_people', show_national_vacancies, show_international_vacancies)
"""

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

def salaries_per_area_view(request, type_):
    show_national_vacancies = False
    show_international_vacancies = False
    if type_ == 'national':
        show_national_vacancies = True
    elif type_ == 'international':
        show_international_vacancies = True
    buffer_value = _get_salaries_per_area_buffer(show_national_vacancies, show_international_vacancies)
    return _get_response_from_buffer_value(buffer_value, 'image/png')
"""
def get_vacancies_and_registered_people_per_area_view(request):
    print('get_chart_view')
    template_name = 'chart/example.html'
    form = None#JobModelForm(request.POST or None)
    print(form)
    national_vacancies_img = _get_vacancies_per_area_image(True, False)
    international_vacancies_img = _get_vacancies_per_area_image(False, True)
    national_registered_people_img = _get_registered_people_per_area_image(True, False)
    international_registered_people_img = _get_registered_people_per_area_image(False, True)
    context = {
        'view_name': 'get_vacancies_and_registered_people_per_area_view',
        'url': '/chart/one_example/',
        'form': form,
        'national_vacancies_img': national_vacancies_img,
        'international_vacancies_img': international_vacancies_img,
        'national_registered_people_img': national_registered_people_img,
        'international_registered_people_img': international_registered_people_img,
    }
    if form != None:
        job = form.save(commit=False)
        try:
            print(dir(form))
            #image_base64 = get_chart_image_base64(11, 25)

            #form_data = form.cleaned_data
            #print(form.cleaned_data)
        except Exception as e:
            print(f'Error: {e}')
            print(dir(form))
        context.update({
            'image_base64': None,
        })

   # return HttpResponse('<img src="/chart/one_example/" width="600px" />')
    return render(request, template_name, context)
    # return response
"""

def _get_vacancies_or_registered_people_per_province_buffer(vacancies_or_registered_people):

    if vacancies_or_registered_people == 'vacancies':
        gdf = get_vacancies_per_province_gdf()
        sub = "Vacantes"
    else:
        gdf = get_registered_people_per_province_gdf()
        sub = "Gente registrada"
    title = f'{sub} por provincias'
    figure = get_spain_map_figure(gdf, vacancies_or_registered_people, title)
    #image_base64 = get_image_base64_from_figure(figure)
   # return image_base64
    img_name = f'{vacancies_or_registered_people}_per_province'
    save_figure_as_image(figure, img_name, _get_images_dir())
    buffer_value = get_buffer_value_from_figure(figure)
    return buffer_value

"""
def _get_vacancies_per_province_buffer():
    return _get_vacancies_or_registered_people_per_province_buffer('vacancies')

def _get_registered_people_per_province_buffer():
    return _get_vacancies_or_registered_people_per_province_buffer('registered_people')
"""

def vacancies_or_registered_people_per_province_view(request, column):
    print('vacancies_or_registered_people_per_province_view')
    print(f'column: {column}')
    buffer_value = _get_vacancies_or_registered_people_per_province_buffer(column)
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

   # execute_preloading()
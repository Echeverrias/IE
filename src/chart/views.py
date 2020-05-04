from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from utilities.utilities import trace
from job.models import Job
from .dataframes import (
    get_initial_queryset,
    get_df,
    merge_spain_gdf_with_df,

)
from .figures import (
    get_buffer_of_bars_from_df,
    get_buffer_of_spain_map,
    get_buffer_of_plot,
    get_spain_map_buffer,
    save_figure_as_image,

)
import os
import threading
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_REQUEST_QUERIES = ['q', 'groupby', 'operator', 'aggregation', 'compareby']

def _get_images_dir():
    return os.path.join(f'static/img/chart/{date.today().month}')


def _get_response_from_buffer_value(buffer_value, content_type):
    response = HttpResponse(buffer_value, content_type=content_type)
    response['Content-Length'] = str(len(response.content))
    return response




#######################################################################################################

def _get_request_parameters(request):
    parameters = dict(request.GET)
    for q_key in POSSIBLE_REQUEST_QUERIES:
        parameters.setdefault(q_key, [])
    print(f'parameters: {parameters}')
    return parameters


def chart_view(request, model, desc):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(f'plot_view:plot/{model}/{desc}')
    parameters = _get_request_parameters(request)
    df = get_df(model, desc, **parameters)
    print(df)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    lgroupby = parameters.get('groupby')
    groupby = lgroupby and lgroupby[0]
    if groupby == 'company':
        df = df.sort_values(parameters.get('aggregation'), ascending=False)[0:15]
       # parameters['groupby'] = [i if i != 'company' else 'name' for i in parameters['groupby']]
    elif groupby == 'province':
        print('/////////////////////////////////////////////////////////////////')
        df = merge_spain_gdf_with_df(df, 'province')
    if groupby == 'province':
        buffer_value = get_buffer_of_spain_map(df,**parameters)
    else:
        buffer_value = get_buffer_of_bars_from_df(df, **parameters)
    return _get_response_from_buffer_value(buffer_value, 'image/png')


def _get_statistics_context():
    available_offers = Job.objects.available_offers()
    national_offers = available_offers.filter(type=Job.TYPE_NATIONAL)
    international_offers = available_offers.filter(type=Job.TYPE_INTERNATIONAL)
    first_job_offers = available_offers.filter(type=Job.TYPE_FIRST_JOB)
    available_offers_size = available_offers.count()
    national_offers_size = national_offers.count()
    international_offers_size = international_offers.count()
    first_job_offers_size = first_job_offers.count()
    available_offers_vacancies = available_offers.aggregate(Sum('vacancies')).get('vacancies__sum')
    national_offers_vacancies = national_offers.aggregate(Sum('vacancies')).get('vacancies__sum')
    international_offers_vacancies = international_offers.aggregate(Sum('vacancies')).get('vacancies__sum')
    first_job_offers_vacancies = first_job_offers.aggregate(Sum('vacancies')).get('vacancies__sum')
    statistics_context = {
        'available_offers': available_offers_size,
        'available_offers_vacancies': available_offers_vacancies,
        'national_offers_vacancies_percentage': round(national_offers_vacancies / available_offers_vacancies, 2),
        'international_offers_vacancies_percentage': round(international_offers_vacancies / available_offers_vacancies, 2),
        'first_job_offers_vacancies_percentage': round(first_job_offers_vacancies / available_offers_vacancies, 2),
    }
    return statistics_context

@login_required
def main_view(request):
    print('main_view')
    template_name = 'chart/main.html'
    context = _get_statistics_context()
    print(f'request.GET: {request.GET}')
    print(f'request.GET.q: {request.GET.get("q")}')
    charts_type = request.GET.get('charts_type')
    print(f'charts_type: {charts_type}')
    get_context = {
        'charts_type': charts_type,
        'month': date.today().month,
        'url': "img/chart/10/national_salaries_per_area.png"
    }
    context = {**context, **get_context}
    # return HttpResponse('<img src="/chart/one_example/" width="600px" />')
    return render(request, template_name, context)


if __name__ != '__main__':

    print('queries - pre_load')
    def _preloading():
     pass

    def execute_preloading():
        images_path = os.path.join(os.path.dirname(_get_images_dir()), str(date.today().month))
        if not os.path.exists(images_path):
            thread = threading.Thread(target=_preloading)
            thread.start()

    #execute_preloading()
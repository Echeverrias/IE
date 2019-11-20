"""
https://django-filter.readthedocs.io/en/master/guide/usage.html#the-filter
https://stackoverflow.com/questions/30366564/daterange-on-a-django-filter
https://stackoverflow.com/questions/21743271/how-to-use-django-filters-datefilter
https://simpleisbetterthancomplex.com/tutorial/2016/11/28/how-to-filter-querysets-dynamically.html
https://simpleisbetterthancomplex.com/tutorial/2019/01/03/how-to-use-date-picker-with-django.html
"""

import django_filters  # pip install django_filter (sin s al final)
from .models import Job
from django.db.models import Q, F
from django import forms
from .widgets import SelectDateWidget
from django.contrib.admin.widgets import AdminDateWidget
from django.views.generic.list import ListView


class JobFilter(django_filters.FilterSet):

    text = django_filters.CharFilter(method='search_text', label='Text')
    minimum_salary = django_filters.NumberFilter(lookup_expr='gte', label='Minimum salary')
    free_vacancies = django_filters.BooleanFilter(method='search_free_vacancies', label='Free vacancies')
    cities = django_filters.CharFilter(field_name="cities", lookup_expr='name__icontains', label='City')
    province = django_filters.CharFilter(field_name="cities", lookup_expr='province__name__icontains', label='Province')
    country = django_filters.CharFilter(field_name="cities", lookup_expr='country__name__icontains', label='Country')
    date = django_filters.DateFilter(field_name='last_update_date',
                                     lookup_expr=('gt'),
                                     label='Fecha posterior',
                                     input_formats=['%d/%m/%Y'],
                                     widget=forms.DateTimeInput(attrs={
                                         'class': 'form-control datetimepicker-input',
                                         'maxlength': 10,
                                         'data-target': '#datetimepicker',
                                         'placeholder': 'dd/mm/aaaa',
                                     }))
    date_range = django_filters.DateRangeFilter(field_name='last_update_date', label="Período de tiempo")
    #date2 = django_filters.DateFilter(method='after_date', label="Fecha posterior", widget=forms.SelectDateWidget)
    #date_between = django_filters.DateFromToRangeFilter(method='between_dates', label='Fecha de oferta')


    class Meta:
        model = Job
        fields = ['id', 'type', 'working_day', 'contract', 'area']


    @property
    def qs(self):
        print('qs')
        parent_qs = super().qs
        return parent_qs.exclude(state__iexact=Job.STATE_CLOSED)

    def search_text(self, queryset, field_name, *args, **kwargs):
        try:
            if args:
                print(f'date: {args[0]}')
                return queryset.filter(Q(name__icontains=args[0])
                                       | Q(requirements__icontains=args[0])
                                       | Q(functions_icontains=args[0])
                                       | Q(it_is_offered__icontains=args[0])
                                       | Q(company__company_name=args[0])).distinct()
        except:
            pass
        return queryset

    def search_free_vacancies(self, queryset, field_name, *args, **kwargs):
        try:
            if args and args[0]:
                return queryset.filter(vacancies__gt=F('registered_people'))
            if args and not args[0]:
                return queryset.filter(vacancies__lte=F('registered_people'))
        except:
            pass
        return queryset

    def after_date(self, queryset, field_name, *args, **kwargs):
        print('after_date')
        print(args)
        try:
            if args:
                print(f'date: {args[0]}')
                return queryset.filter(Q(last_update_date__gte=args[0])).distinct()
        except:
            pass
        return queryset

    def between_dates(self, queryset, field_name, *args, **kwargs):
        print('between dates')
        print(args)
        try:
            if args:
                slice=args[0]
                print(f'date: {args[0]}')
                qs_start = queryset.filter(Q(first_publication_date__gte=slice.start)
                                       | Q(last_update_date__gte=slice.start)).distinct()
                return qs_start.filter(Q(first_publication_date__lte=slice.stop)
                                           | Q(last_update_date__lte=slice.stop)).distinct()
        except:
            pass
        return queryset




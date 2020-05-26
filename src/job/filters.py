from django.utils.translation import ugettext_lazy as _
import django_filters
from .models import Job
from django.db.models import Q, F
from datetime import date
from django import forms
import logging
logging.getLogger().setLevel(logging.INFO)

MONTHS = {
    1:_('Enero'), 2:_('Febrero'), 3:_('Marzo'), 4:_('Abril'),
    5:_('Mayo'), 6:_('Junio'), 7:_('Julio'), 8:_('Agosto'),
    9:_('Septiembre'), 10:_('Octubre'), 11:_('Noviembre'), 12:_('Diciembre')
}

def _get_offers_years_range():
    try:
        early_offer_year = Job.objects.exclude(first_publication_Date=None).earliest(
            'first_publication_date').first_publication_date.year
        latest_offer_year = Job.objects.latest('first_publication_date').first_publication_date.year
    except:
        year = date.today().year
        return range(year, year + 1)
    else:
        return range(early_offer_year, latest_offer_year)


class JobFilter(django_filters.FilterSet):

    class Meta:
        model = Job
        fields = ['type', 'working_day', 'contract', 'area']

    free_vacancies = django_filters.BooleanFilter(method='search_free_vacancies', label='Vacantes libres')
    text = django_filters.CharFilter(method='search_text', label='Texto')
    minimum_salary = django_filters.NumberFilter(lookup_expr='gte', label='Salario mínimo')
    cities = django_filters.CharFilter(field_name="cities", lookup_expr='name__icontains', label='Ciudad')
    province = django_filters.CharFilter(field_name="cities", lookup_expr='province__name__icontains', label='Provincia')
    country = django_filters.CharFilter(field_name="cities", lookup_expr='country__name__icontains', label='País')
    datepicker = django_filters.DateFilter(method='after_date',
                                           label="Fecha posterior",
                                           widget=forms.SelectDateWidget(
                                               months = MONTHS,
                                               years=_get_offers_years_range(),
                                               empty_label=("Elige año", "Elige mes", "Elige día"),
                                           ))
    #date_range = django_filters.DateRangeFilter(field_name='last_update_date', label="Período de tiempo")

    @property
    def qs(self):
        parent_qs = super(JobFilter, self).qs
        return parent_qs

    def search_free_vacancies(self, queryset, field_name, *args, **kwargs):
        try:
            if args and args[0]:
               return queryset.free_vacancies()
            if args and not args[0]:
                return queryset.not_free_vacancies()
        except Exception:
            logging.exception("Error in search_text")
        return queryset

    def search_text(self, queryset, field_name, *args, **kwargs):
        try:
            if args:
                qs = queryset.filter(Q(name__icontains=args[0])
                                       | Q(requirements__icontains=args[0])
                                       | Q(functions__icontains=args[0])
                                       | Q(it_is_offered__icontains=args[0])
                                       | Q(company__name=args[0]))
                qs = qs.distinct()
                return qs
        except Exception as e:
            logging.exception("Error in search_text")
            return Job.objects.none()
        return queryset

    def after_date(self, queryset, field_name, *args, **kwargs):
        try:
            if args:
                return queryset.filter(Q(last_update_date__gte=args[0]) |
                                       Q(first_publication_date__gte=args[0])).distinct()
        except Exception:
            logging.exception("Error in search_text")
        return queryset

    def between_dates(self, queryset, field_name, *args, **kwargs):
        print('between dates')
        print(args)
        try:
            if args:
                slice=args[0] # django_filters.DateFromToRangeFilter return a slice with the dates
                qs_start = queryset.filter(Q(first_publication_date__gte=slice.start)
                                       | Q(last_update_date__gte=slice.start)).distinct()
                return qs_start.filter(Q(first_publication_date__lte=slice.stop)
                                           | Q(last_update_date__lte=slice.stop)).distinct()
        except Exception:
            logging.exception("Error in search_text")
        return queryset
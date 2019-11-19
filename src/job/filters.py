# pip install django_filter (sin s al final)
import django_filters
from .models import Job
from django.db.models import Q
from django.views.generic.list import ListView

class JobFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name')
    minimum_salary = django_filters.NumberFilter(lookup_expr='gte', label='Minimum salary')
    cities = django_filters.CharFilter(field_name="cities", lookup_expr='name__icontains', label='City')
    province = django_filters.CharFilter(field_name="province", method='cities__province__name', label='Province')
    country = django_filters.CharFilter(field_name="country", method='cities__country__name', label='Country')
    date = django_filters.DateFilter(field_name="date", method='after_date', label='Date')

    class Meta:
        model = Job
        fields = ['type', 'working_day', 'contract', 'area']

    def cities__country__name(self, queryset, field_name, *args, **kwargs):
        try:
            if args:
                return queryset.filter(cities__country__name__icontains=args[0])
        except:
            pass
        return queryset

    def cities__province__name(self, queryset, field_name, *args, **kwargs):
        try:
            if args:
                return queryset.filter(cities__province__name__icontains=args[0])
        except:
            pass
        return queryset

    def after_date(self, queryset, field_name, *args, **kwargs):
        try:
            if args:
                return queryset.filter(Q(created_at__gte=args[0]), Q(updated_at__gte=args[0]))
        except:
            pass
        return queryset


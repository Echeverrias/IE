"""ie_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import (
     main_view,
     vacancies_or_registered_people_per_area_view,
     vacancies_and_registered_people_per_area_view,
     national_and_international_vacancies_or_registered_people_per_area_view,
     vacancies_or_registered_people_per_province_view,
     salaries_per_area_view,
     salaries_per_province_view,
     national_and_international_salaries_per_area_view,
)



urlpatterns = [
     path('', main_view, name='main'),
     path('vacancies-or-registered-people-per-area/<str:type_>/<str:column>/', vacancies_or_registered_people_per_area_view, name='vacancies_or_registered_people_per_area'),
     path('vacancies-and-registered-people-per-area/<str:type_>/', vacancies_and_registered_people_per_area_view, name='vacancies_and_registered_people_per_area'),
     path('national-and-international-vacancies-or-registered-people-per-area/<str:column>/', national_and_international_vacancies_or_registered_people_per_area_view, name='national_and_international_vacancies_or_registered_people_per_area'),
     path('salaries-per-area/<str:type_>/', salaries_per_area_view, name='salaries_per_area'),
     path('salaries-per-province/', salaries_per_province_view, name='salaries_per_province'),
     path('national-and-international-salaries-per-area/', national_and_international_salaries_per_area_view, name='national_and_international_salaries_per_area'),
     path('vacancies-or-registered-people-per-province/<str:column>/', vacancies_or_registered_people_per_province_view, name='vacancies_or_registered_people_per_province'),
]

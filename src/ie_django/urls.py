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
from django.contrib import admin
from django.urls import path
from dataset.views import get_jobs_view
from jobs.views import JobAPIView, CompanyAPIView, JobView, CompanyView, welcome_view, set_spain_locations_view, delete_companies_and_jobs_view, query_view, run_crawler
urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('crawl/', run_crawler, name='crawl'),
    path('dataset/', get_jobs_view, name='dataset'),
    path(r'jobs/', JobView.as_view(), name='jobs2'),
    path(r'companies/', CompanyView.as_view(), name='companies2'),
    path(r'api/jobs/', JobAPIView.as_view(), name='jobs'),
    path(r'api/companies/', CompanyAPIView.as_view(), name='companies'),
    path(r'insert_locations', set_spain_locations_view, name='locations'),
    path(r'reset', delete_companies_and_jobs_view, name='delete'),
    path(r'query', query_view, name='query'),
    path('', welcome_view, name='welcome'),
]

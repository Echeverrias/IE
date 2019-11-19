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
from django.urls import  include, path, re_path #url, re_url
from .views import init_view
from job.views import  run_crawler
#from job.views import JobAPIView, CompanyAPIView, JobView, CompanyView,
urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('crawl/', run_crawler, name='crawl'),
    path('chart/', include('chart.urls')),
    path('job/', include('job.urls')),
    path('task/', include('task.urls')),
    path('', init_view, name='init'),
]

"""
  re_path(r'job/', JobView.as_view(), name='jobs2'),
    re_path(r'companies/', CompanyView.as_view(), name='companies2'),
    re_path(r'api/job/', JobAPIView.as_view(), name='job'),
    re_path(r'api/companies/', CompanyAPIView.as_view(), name='companies'),
"""

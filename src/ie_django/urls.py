from django.contrib import admin
from django.urls import  include, path, re_path #url, re_url
from django.views.generic import RedirectView
from .views import init_view

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('job/', include('job.urls')),
    path('task/', include('task.urls')),
    path('account/', include('account.urls')),
    path('home/', init_view, name='home'),
    path('', RedirectView.as_view(url='/home', permanent=True)),
]

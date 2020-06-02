from django.contrib import admin
from django.urls import  include, path, re_path
from django.views.generic import RedirectView
from django.contrib.staticfiles.views import serve as serve_static
from django.conf import settings

from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('job/', include('job.urls')),
    path('task/', include('task.urls')),
    path('account/', include('account.urls')),
    path('home/', home_view, name='home'),
    re_path(r'^$', RedirectView.as_view(url='/home', permanent=True), name='home'),
    path('', RedirectView.as_view(url='/home', permanent=True),  name='home'),
]
handler404 = 'ie_django.views.handler404'
handler500 = 'ie_django.views.handler500'
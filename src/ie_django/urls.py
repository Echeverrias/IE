from django.contrib import admin
from django.urls import  include, path, re_path
from django.views.generic import RedirectView
from django.contrib.staticfiles.views import serve as serve_static
from .views import home_view

def _static_butler(request, path, **kwargs):
    """
    Serve static files using the django static files configuration.
    Passing insecure=True allows serve_static to process, and ignores
    the DEBUG=False setting
    """
    return serve_static(request, path, insecure=True, **kwargs)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('job/', include('job.urls')),
    path('task/', include('task.urls')),
    path('account/', include('account.urls')),
    path('home/', home_view, name='home'),
    re_path(r'staticfiles/(.+)', _static_butler),
    re_path(r'^$', RedirectView.as_view(url='/home', permanent=True), name='home'),
    path('', RedirectView.as_view(url='/home', permanent=True),  name='home'),
]

handler404 = 'ie_django.views.handler404'
handler500 = 'ie_django.views.handler500'
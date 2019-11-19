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
from .views import bg_task_view, bg2, bg3, bg4
urlpatterns = [
    path('bg1/', bg_task_view, name='bg1'),
    path('bg2/', bg2, name='bg2'),
    path('bg3/', bg3, name='bg3'),
    path('bg4/', bg4, name='bg4'),
    path('bg5/', bg_task_view, name='bg5'),

]


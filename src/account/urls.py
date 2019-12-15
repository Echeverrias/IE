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
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from .views import (
    signin_view,
    login_view,
)

urlpatterns = [
    path('signin/', signin_view, name='signin'),
    path('login/',  login_view , name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/', PasswordResetView.as_view(
        template_name='account/password_reset.html',
        email_template_name='account/password_reset_email.html',
        subject_template_name='account/password_reset_subject.txt'
    ), name='password_reset'),
    path('reset/done/', PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html',
    ), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/complete/', PasswordResetCompleteView.as_view(
       template_name='account/password_reset_complete.html'
    ), name='password_reset_complete'),
    path(r'settings/password/', PasswordChangeView.as_view(template_name='account/password_change.html'),
    name='password_change'),
    path(r'settings/password/done/', PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'),
    name='password_change_done'),
]


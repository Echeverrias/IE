from django.urls import  include, path, re_path
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
    path('login/', LoginView.as_view(
        template_name='account/login.html',
    ), name='login'),
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


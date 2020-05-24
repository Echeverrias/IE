from django.urls import  include, path, re_path
from django.contrib.auth.views import LoginView,LogoutView
from .views import register_view, login_view
from django.views.generic import RedirectView

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/',  login_view , name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

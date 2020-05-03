from django.urls import path, re_path
from .views import run_crawler_view

urlpatterns = [
    path('scraping/', run_crawler_view, name='choose_spider'),
    path('scraping/<str:model>/', run_crawler_view, name='run_crawler'),
]


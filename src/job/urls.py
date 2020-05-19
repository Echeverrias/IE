from django.urls import path
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from .views import JobListView
from .models import Job

urlpatterns = [
    path("list/", JobListView.as_view(), name='job_list'),
    path("detail/<int:pk>/", login_required(DetailView.as_view(model=Job)), name='job_detail'),
]

"""
# from django_filters.views import FilterView
# path("filter-job/", FilterView.as_view(filterset_class=JobFilter, template_name='job/filter_form.html'), name='filter_job'),
"""
from django.urls import path
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from .views import JobListView
from .models import Job

urlpatterns = [
    path("list/", JobListView.as_view(), name='job_list'),
    path("detail/<int:pk>/", login_required(DetailView.as_view(model=Job)), name='job_detail'),
]
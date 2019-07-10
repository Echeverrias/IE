from django.shortcuts import render

# Create your views here.
from jobs.models import Company, Job
from django.http import HttpResponse

def get_jobs_view(request):
    jobs = Job.objects.all()
    jobs_list = []
    for j in jobs:
        jobs_list.append(j.name)
    context = {
        'jobs_list': jobs_list,
        'jobs_number': Job.objects.all().count()
    }
    return render(request, 'dataset.html', context)



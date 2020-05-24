from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Job
from .filters import JobFilter

@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    model = Job
    context_object_name = 'job_list'
    template_name = 'job/query_form.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        print(f'JobListView.get_queryset')
        qs = super(JobListView, self).get_queryset()
        qs = qs.prefetch_related('cities')
        self.job_filtered_list = JobFilter(self.request.GET, qs)
        return self.job_filtered_list.qs

    def get_context_data(self, **kwargs):
        context = super(JobListView, self).get_context_data(**kwargs)
        context['form'] = self.job_filtered_list.form
        return context


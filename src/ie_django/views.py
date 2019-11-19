
from django.shortcuts import render
from django.http import HttpResponse



def init_view(request):
    template_name="init.html"
    return render(request, template_name)

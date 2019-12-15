
from django.shortcuts import render, redirect
from django.http import HttpResponse



def init_view(request):
    print('init_view')
    print(f'request.user.is_authenticated: {request.user.is_authenticated}')
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        template_name = "init.html"
        return render(request, template_name)

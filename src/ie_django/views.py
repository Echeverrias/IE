from django.shortcuts import render, redirect

def home_view(request):
    template_name = "index.html"
    return render(request, template_name) #% Delete for production
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, template_name)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
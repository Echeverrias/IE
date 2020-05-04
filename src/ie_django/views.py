from django.shortcuts import render, redirect

def init_view(request):
    template_name = "index.html"
    return render(request, template_name) #% Delete for production
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, template_name)
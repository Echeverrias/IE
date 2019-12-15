from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from .forms import SignInForm

def signin_view(request):
    template_name = "account/signin.html"
    if (request.method == 'POST'):
        form = SignInForm(request.POST)
        if form.is_valid():
            user = form.save()
            """
            login(request, user)
            """
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('home')
    else: # GET request
        form = SignInForm()
    context = {'form': form}
    return render(request, template_name, context)

def login_view(request, **kwargs):
    if request.user.is_authenticated:
        return redirect('/home/')
    else:
        return auth_views.LoginView.as_view(template_name="account/login.html")(request)


def logout_view(request):
    logout(request)
    return redirect('home')
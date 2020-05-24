from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from .forms import SignUpForm

def signup_view(request):
    template_name = "account/signup.html"
    if (request.method == 'POST'):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username, raw_password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
            account = authenticate(username=username, password=raw_password)
            user.email_user('Bienvenido a IE', f'Bienvenido {user.username}, te has registrado con éxito.')
            login(request, account)
            #login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/home/')
    else: # GET request
        form = SignUpForm()
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
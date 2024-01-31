from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from .models import User


# Create your views here.


def register_view(request):
    """ parse and handle registration form """
    user_already_exists = False
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            if User.objects.filter(username=request.POST.get('username')).exists():
                user_already_exists = True

    form = UserCreationForm()
    return render(request, 'register.html', {'form': form, 'user_already_exists': user_already_exists})


def login_view(request):
    """ login user to session """
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            request.session['is_master_editor'] = request.user.groups.filter(name='MasterEditors').exists()
            request.session['is_editor'] = request.user.groups.filter(name='Editors').exists()
            return redirect(request.GET.get('next', 'home'))

    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

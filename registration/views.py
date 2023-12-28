from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


# Create your views here.


def register_view(request):
    """parse and handle registration form"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """ login user to session """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            is_master_editor = request.user.groups.filter(name='MasterEditors').exists()
            request.session['is_master_editor'] = bool(is_master_editor)
            is_editor = request.user.groups.filter(name='Editors').exists()
            request.session['is_editor'] = bool(is_editor)
            return redirect(request.GET.get('next', 'home'))

    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

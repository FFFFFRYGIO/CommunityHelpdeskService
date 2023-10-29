from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group


# Create your views here.


def register_view(request):
    """parse and handle registration form"""
    messages = []
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(Group.objects.get(name='Users'))
            return redirect("login")
        else:
            return render(request, "register.html", {"form": form, "messages": messages})
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form, "messages": messages})


def login_view(request):
    messages = []
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.append("Wrong username or password")
            return render(request, "login.html")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form, "messages": messages})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

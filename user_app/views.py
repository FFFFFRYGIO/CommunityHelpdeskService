from django.shortcuts import render

# In your views.py


def home(request):
    return render(request, 'home.html')


def search(request):
    return render(request, 'search.html')


def create_article(request):
    return render(request, 'create_article.html')


def edit_article(request):
    return render(request, 'edit_article.html')


def create_report(request):
    return render(request, 'create_report.html')


def user_panel(request):
    return render(request, 'user_panel.html')

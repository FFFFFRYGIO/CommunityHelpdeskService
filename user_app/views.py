from django.shortcuts import render

# In your views.py


def home_view(request):
    return render(request, 'home.html')


def search_view(request):
    return render(request, 'search.html')


def create_article_view(request):
    return render(request, 'create_article.html')


def edit_article_view(request):
    return render(request, 'edit_article.html')


def create_report_view(request):
    return render(request, 'create_report.html')


def user_panel_view(request):
    return render(request, 'user_panel.html')

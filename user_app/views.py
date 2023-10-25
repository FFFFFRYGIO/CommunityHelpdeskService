from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# In your views.py


def home_view(request):
    return render(request, 'home.html')


def search_view(request):
    return render(request, 'search.html')


@login_required
def create_article_view(request):
    return render(request, 'create_article.html')


@login_required
def edit_article_view(request, article_id):

    return render(request, 'edit_article.html')


@login_required
def create_report_view(request):
    return render(request, 'create_report.html')


@login_required
def user_panel_view(request):
    return render(request, 'user_panel.html')

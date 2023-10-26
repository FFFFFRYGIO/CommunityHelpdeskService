from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# In your views.py


def home_view(request):
    return render(request, 'home.html')


def search_view(request):
    return render(request, 'search.html')


@login_required
def create_article_view(request):
    article_form = set()  # TODO: parse article creation form
    return render(request, 'create_article.html', {'article_form': article_form})


@login_required
def edit_article_view(request, article_id):
    article_form = []  # TODO: parse article creation form
    # TODO: verify that user is owner of ther article
    article = article_id  # TODO: get article from article_id
    return render(request, 'edit_article.html', {'article': article, 'article_form': article_form})


@login_required
def create_report_view(request, article_id):
    report_form = []  # TODO: parse report creation form
    return render(request, 'create_report.html', {'article_id': article_id, 'report_form': report_form})


@login_required
def user_panel_view(request):
    user_articles = []  # TODO: parse user articles
    user_reports = []  # TODO: parse user reports
    return render(request, 'user_panel.html')

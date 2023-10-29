from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ArticleForm, SearchByNameForm, SearchByTagsForm
import datetime

# In your views.py


def home_view(request):
    return render(request, 'home.html')


def search_view(request):
    return render(request, 'search.html', {
        'form': ArticleForm, 'search_name_form': SearchByNameForm, 'search_tags_form': SearchByTagsForm})


@login_required
def create_article_view(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.created_at = datetime.datetime.now()
            new_article.save()
            return redirect('home')
    return render(request, 'create_article.html', {'form': ArticleForm})


@login_required
def edit_article_view(request, article_id):
    article_form = []  # TODO: parse article creation form
    # TODO: verify that user is owner of the article
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

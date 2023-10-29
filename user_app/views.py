from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ArticleForm, SearchByNameForm, SearchByTagsForm
from .models import Article
import datetime
from taggit.models import Tag
from django.http import HttpResponse
from django.db.models import Q


# In your views.py


def home_view(request):
    return render(request, 'home.html')


def search_view(request):
    search_result = []

    if request.method == "POST":
        if 'search_name' in request.POST:
            search_name_form = SearchByNameForm(request.POST)
            if search_name_form.is_valid():
                search_text = search_name_form.cleaned_data['search_text']
                search_result = Article.objects.filter(title__icontains=search_text)

        if 'search_tags' in request.POST:
            search_tags_form = SearchByTagsForm(request.POST)
            if search_tags_form.is_valid():
                tags_to_search = search_tags_form.cleaned_data['tags']
                tag_objects = Tag.objects.filter(name__in=tags_to_search)
                search_result = Article.objects.filter(tags__in=tag_objects)

        if 'search_ownership' in request.POST:
            if request.user.is_authenticated:
                search_result = Article.objects.filter(Q(author=request.user))
            else:
                return HttpResponse("HTTP Unauthorized", status=401)

    return render(request, 'search.html', {
        'search_name_form': SearchByNameForm, 'search_tags_form': SearchByTagsForm, 'search_result': search_result})


@login_required
def create_article_view(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.created_at = datetime.datetime.now()
            new_article.save()

            tags = request.POST.get('tags')
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                new_article.tags.set(tag_list)

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

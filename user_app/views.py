from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ArticleForm, StepForm, StepFormSet, SearchByNameForm, SearchByTagsForm
from .models import Article, Step
from datetime import datetime
from taggit.models import Tag
from django.http import HttpResponse
from django.db.models import Q
from editor_app.models import Report
from editor_app.forms import ReportForm
from registration.models import User


# In your views.py


def home_view(request):
    """ home page, default redirection from other pages """
    return render(request, 'home.html')


def search_view(request):
    """ search articles to view them """
    search_result = []

    if request.method == "POST":
        if 'search_title' in request.POST:
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
    """ a form to create an article """
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.created_at = datetime.now()
            new_article.status = "unapproved"
            new_article.save()

            tags = request.POST.get('tags')
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                new_article.tags.set(tag_list)

            step_form_set = StepFormSet(request.POST)
            if step_form_set.is_valid():
                ordinal_number = 1
                for step_form in step_form_set:
                    step_data = step_form.save(commit=False)
                    if step_data.title:
                        step = Step()
                        step.article = new_article
                        step.ordinal_number = ordinal_number
                        step.title = step_data.title
                        step.description1 = step_data.description1
                        step.file1 = step_data.file1
                        step.description2 = step_data.description2
                        step.file2 = step_data.file2
                        step.save()
                        ordinal_number += 1

                new_report = Report()
                new_report.description = f"Review new article {new_article.title}"
                new_report.author = User.objects.get(username='system_automat')
                new_report.created_at = datetime.now()
                new_report.article = new_article
                new_report.status = "new article"
                new_report.save()

                return redirect('home')

    article_form = ArticleForm()
    step_form_set = StepFormSet(queryset=Step.objects.none())
    return render(request, 'create_article.html', {'article_form': article_form, 'step_form_set': step_form_set})


def view_article_view(request, article_id):
    """ view or report an article """
    article = Article.objects.get(id=article_id)
    can_edit = request.user == article.author or Report.objects.filter(article=article, editor=request.user).exists()
    steps = Step.objects.filter(article=article).order_by('ordinal_number')
    return render(request, 'view_article.html', {'article': article, 'steps': steps, 'can_edit': can_edit})


@login_required
def edit_article_view(request, article_id):
    """ change article elements (for owners and editors) """
    article = Article.objects.get(id=article_id)
    if request.user == article.author or Report.objects.filter(article=article, editor=request.user).exists():
        if request.method == 'POST':
            article_form = ArticleForm(request.POST, instance=article)
            if article_form.is_valid():
                article_form.save()
                return redirect('home')
        else:
            article_form = ArticleForm(instance=article)
        return render(request, 'edit_article.html', {'article': article, 'article_form': article_form})

    return redirect('home')


@login_required
def user_panel_view(request):
    """ all user's articles and reports """
    user_articles = Article.objects.filter(author=request.user)
    user_reports = Report.objects.filter(author=request.user)
    return render(request, 'user_panel.html', {'articles': user_articles, 'reports': user_reports})


@login_required
def report_article_view(request, article_id):
    """ a form to create report about specified article """
    article = Article.objects.get(id=article_id)

    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.author = request.user
            report.article = article
            report.created_at = datetime.now()
            report.status = "Created"
            report.save()
            return redirect('home')

    else:
        report_form = ReportForm(initial={'article': article})
        return render(request, 'report_article.html', {'article': article, 'report_form': report_form})


@login_required
def view_report_view(request, report_id):
    """ view the whole content of the report """
    report = Report.objects.get(id=report_id)

    if report.author == request.user:
        return render(request, 'view_report.html', {'report': report})

    else:
        return redirect("home")

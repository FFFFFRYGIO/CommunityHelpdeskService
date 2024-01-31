from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from taggit.models import Tag

from CommunityHelpdeskService.utils import save_files, generate_report_title, ArticleStatus, ReportStatus
from editor_app.forms import ReportForm
from editor_app.models import Report
from registration.models import User
from .forms import ArticleForm, StepFormSetCreate, StepFormSetEdit, SearchByTitleForm, SearchByPhraseForm, \
    SearchByTagsForm
from .models import Article, Step


# In your views.py


def home_view(request):
    """ home page, default redirection from other pages """
    return render(request, 'home.html')


def search_view(request):
    """ search articles to view them """
    searched_articles = []
    search_result = []

    if request.method == 'POST':
        if 'search_by_title' in request.POST:
            search_title_form = SearchByTitleForm(request.POST)
            if search_title_form.is_valid():
                search_text = search_title_form.cleaned_data['search_title']
                search_permitted_statuses = [status.n for status in ArticleStatus if status.search_permitted]
                searched_articles = Article.objects.filter(
                    title__icontains=search_text, status__in=search_permitted_statuses)
            else:
                return HttpResponseBadRequest(f'form not valid: {search_title_form.errors}')

        if 'search_by_phrase' in request.POST:
            search_phrase_form = SearchByPhraseForm(request.POST)
            if search_phrase_form.is_valid():
                search_text = search_phrase_form.cleaned_data['search_phrase']
                search_permitted_statuses = [status.n for status in ArticleStatus if status.search_permitted]

                searched_articles = Article.objects.filter(
                    Q(status__in=search_permitted_statuses) & (
                            Q(title__icontains=search_text) |
                            Q(step__title__icontains=search_text) |
                            Q(step__description1__icontains=search_text) |
                            Q(step__description2__icontains=search_text)
                    )
                ).distinct()

            else:
                return HttpResponseBadRequest(f'form not valid: {search_phrase_form.errors}')

        if 'search_by_tags' in request.POST:
            search_tags_form = SearchByTagsForm(request.POST)
            if search_tags_form.is_valid():
                tags_to_search = search_tags_form.cleaned_data['search_tags']
                tag_objects = Tag.objects.filter(name__in=tags_to_search)
                searched_articles = Article.objects.filter(tags__in=tag_objects)
            else:
                return HttpResponseBadRequest(f'form not valid: {search_tags_form.errors}')

        if 'search_by_ownership' in request.POST:
            if request.user.is_authenticated:
                searched_articles = Article.objects.filter(Q(author=request.user))
            else:
                return HttpResponse('HTTP Unauthorized', status=401)

        search_result = ({
            'article': article,
            'steps_amount': len(Step.objects.filter(article=article)),
        } for article in searched_articles)

    return render(request, 'search.html', {
        'search_title_form': SearchByTitleForm, 'search_phrase_form': SearchByPhraseForm,
        'search_tags_form': SearchByTagsForm, 'search_result': search_result})


@login_required
def create_article_view(request):
    """ a form to create an article """
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.status = ArticleStatus.UNAPPROVED.n
            new_article.save()

            tags = request.POST.get('tags')
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                new_article.tags.set(tag_list)

            step_form_set = StepFormSetCreate(request.POST, request.FILES)
            if step_form_set.is_valid():
                save_files(request.FILES)
                ordinal_number = 1
                for step_form in step_form_set:
                    step = step_form.save(commit=False)
                    step.article = new_article
                    step.ordinal_number = ordinal_number
                    step.save()
                    ordinal_number += 1

                new_report = Report()
                new_report.title = f'Review "{new_article.title}"'
                new_report.description = f'Review new article "{new_article.title}"'
                new_report.author = User.objects.get(username='system_automat')
                new_report.article = new_article
                new_report.status = ReportStatus.NA_OPENED.n
                with open('CommunityHelpdeskService/static/img/favicon.png', 'rb') as image:
                    content_file = ContentFile(image.read())
                    new_report.additional_file.save('favicon.png', content_file)
                new_report.save()

                return redirect('home')

            else:
                return HttpResponseBadRequest(f'step_form_set not valid: {step_form_set.errors}')

        else:
            return HttpResponseBadRequest(f'article creation form not valid: {form.errors}')

    article_form = ArticleForm()
    step_form_set = StepFormSetCreate(queryset=Step.objects.none())
    return render(request, 'manage_article.html',
                  {'article_form': article_form, 'step_form_set': step_form_set, 'type': 'Create'})


def view_article_view(request, article_id):
    """ view or report an article """
    article = Article.objects.get(id=article_id)
    if request.user.is_authenticated:
        can_edit_author = request.user == article.author
        can_edit_editor = Report.objects.filter(article=article, editor=request.user).exists()
        can_edit = can_edit_author or can_edit_editor
    else:
        can_edit = False
    steps = Step.objects.filter(article=article).order_by('ordinal_number')
    status = ArticleStatus.get_status_name(article.status)
    return render(request, 'view_article.html',
                  {'article': article, 'steps': steps, 'status': status, 'can_edit': can_edit})


@login_required
def edit_article_view(request, article_id):
    """ change article elements (for owners and editors) """
    article = Article.objects.get(id=article_id)
    if request.user == article.author or Report.objects.filter(article=article, editor=request.user).exists():
        if request.method == 'POST':

            article_form = ArticleForm(request.POST, instance=article)
            if not article_form.is_valid():
                return HttpResponseBadRequest(f'article_form not valid: {article_form.errors}')

            article_form.save()

            original_steps = Step.objects.filter(article=article)

            step_form_set = StepFormSetEdit(request.POST, request.FILES, queryset=Step.objects.filter(article=article))

            ordinal_number = 1
            for step_form in step_form_set:
                try:
                    step = original_steps.get(ordinal_number=ordinal_number)
                except Step.DoesNotExist:
                    step = Step()
                    step.article = article
                    step.ordinal_number = ordinal_number

                step.title = step_form.data.get(f'form-{ordinal_number - 1}-title')
                step.description1 = step_form.data.get(f'form-{ordinal_number - 1}-description1')
                step.description2 = step_form.data.get(f'form-{ordinal_number - 1}-description2')

                if request.FILES.get(f'form-{ordinal_number - 1}-file1'):
                    step.file1 = request.FILES.get(f'form-{ordinal_number - 1}-file1')
                elif step_form.data.get(f'form-{ordinal_number - 1}-file1-clear'):
                    step.file1 = request.FILES.get(f'form-{ordinal_number - 1}-file1')

                if request.FILES.get(f'form-{ordinal_number - 1}-file2'):
                    step.file2 = request.FILES.get(f'form-{ordinal_number - 1}-file2')
                elif step_form.data.get(f'form-{ordinal_number - 1}-file2-clear'):
                    step.file2 = request.FILES.get(f'form-{ordinal_number - 1}-file2')

                ordinal_number += 1

                step.save()

            steps_to_delete = Step.objects.filter(article=article, ordinal_number__gte=ordinal_number)
            steps_to_delete.delete()

            if request.user.groups.filter(name='Editors').exists():
                for report in Report.objects.filter(article=article, editor=request.user):
                    if report.status in (ReportStatus.NA_ASSIGNED.n, ReportStatus.ASSIGNED.n):
                        article.status = ArticleStatus.CHANGES_DURING_REPORT.n
                        # change from '(na) assigned' to '(na) changes applied' for both types of report
                        report.status += 1
                        report.save()

            else:
                article.status = ArticleStatus.UNAPPROVED.n

                new_report = Report()
                new_report.title = f'Review changes in "{article.title}"'
                new_report.description = (f'Owner applied changes in this article: "{article.title}", it is '
                                          f'required to review them')
                new_report.author = User.objects.get(username='system_automat')
                new_report.article = article
                new_report.status = ReportStatus.NA_OPENED.n
                with open('CommunityHelpdeskService/static/img/favicon.png', 'rb') as image:
                    content_file = ContentFile(image.read())
                    new_report.additional_file.save('favicon.png', content_file)
                new_report.save()

            article.save()
            return redirect('home')
        else:
            article_form = ArticleForm(instance=article)
            step_form_set = StepFormSetEdit(queryset=Step.objects.filter(article=article))
        return render(request, 'manage_article.html', {
            'article': article, 'article_form': article_form, 'step_form_set': step_form_set, 'type': 'Edit'})

    return redirect('home')


@login_required
def user_panel_view(request):
    """ all user's articles and reports """

    user_articles = [{
        'article': article, 'steps_amount': len(Step.objects.filter(article=article)),
    } for article in Article.objects.filter(author=request.user)]

    view_permitted_statuses = [status.n for status in ReportStatus if status.view_permitted]
    user_authored_reports = Report.objects.filter(author=request.user, status__in=view_permitted_statuses)
    users_article_reports = Report.objects.filter(article__author=request.user, status__in=view_permitted_statuses)
    user_reports_list = (user_authored_reports | users_article_reports).distinct()
    user_reports = [{
        'report': report, 'report_status': ReportStatus.get_status_name(report.status),
    } for report in user_reports_list]

    return render(request, 'user_panel.html',
                  {'articles_with_steps': user_articles, 'reports_with_status': user_reports})


@login_required
def report_article_view(request, article_id):
    """ a form to create a report about specified article """
    article = Article.objects.get(id=article_id)
    steps = Step.objects.filter(article=article).order_by('ordinal_number')

    if request.method == 'POST':
        report_form = ReportForm(request.POST, request.FILES)
        if report_form.is_valid():
            save_files(request.FILES)
            report = report_form.save(commit=False)
            report.title = generate_report_title(report.description)
            report.author = request.user
            report.article = article
            report.status = ReportStatus.OPENED.n
            report.save()

            article.status = ArticleStatus.CHANGES_REQUESTED.n
            article.save()

            return redirect('home')

        else:
            return HttpResponseBadRequest(f'report not valid: {report_form.errors}')

    else:
        report_form = ReportForm(initial={'article': article})
        return render(request, 'report_article.html', {'report_form': report_form, 'article': article, 'steps': steps})


@login_required
def view_report_view(request, report_id):
    """ view the whole content of the report """
    report = Report.objects.get(id=report_id)

    if report.author == request.user or report.article.author == request.user:
        status = ReportStatus.get_status_name(report.status)
        return render(request, 'view_report.html', {'report': report, 'status': status})

    else:
        return redirect('home')

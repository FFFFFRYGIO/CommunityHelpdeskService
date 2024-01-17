from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from parameterized import parameterized

from CommunityHelpdeskService.utils import ReportStatus, ArticleStatus
from editor_app.forms import ReportForm
from editor_app.models import Report
from tests.MainTestBase import MainTestBase, USERS, FORM_DATA
from user_app.forms import StepFormSetCreate
from user_app.models import Article, Step


# Create your tests here.


class StatusesTests(MainTestBase):
    def user_create_article(self):
        """ Create article to be reported"""
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[0]['username'], 'password': USERS[0]['password']})
        self.assertRedirects(response, reverse('home'))

        step_form_set = StepFormSetCreate(FORM_DATA)
        self.assertTrue(step_form_set.is_valid(), f'step_form_set not valid: {step_form_set.errors}')
        response = self.client.post(reverse('create_article'), data=FORM_DATA)

        self.assertRedirects(response, reverse('home'))
        articles = Article.objects.filter(title=FORM_DATA['title'])
        self.assertEqual(len(articles), 1)
        self.assertEqual(len(Step.objects.filter(article=articles[0])), 2)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        report = Report.objects.get(article__title=FORM_DATA['title'])
        self.assertEqual(report.status, ReportStatus.NA_OPENED.n)
        self.assertEqual(report.article.status, ArticleStatus.UNAPPROVED.n)

    def user_report_article(self):
        """ Create the report about the existing article"""
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[1]['username'], 'password': USERS[1]['password']})
        self.assertRedirects(response, reverse('home'))

        articles = Article.objects.filter(title=FORM_DATA['title'])
        self.assertEqual(len(articles), 1)
        article = articles[0]

        file_path = 'tests/test_sources/test_image.png'
        with open(file_path, 'rb') as file:
            file_content = file.read()
            file_name = 'test_image.png'
            file_data = SimpleUploadedFile(file_name, file_content, content_type='image/png')

        report_data = {
            'description': f'New report about article "{FORM_DATA["title"]}"',
            'article': article,
            'additional_file': file_data,
        }

        report_files = {'additional_file': file_data}
        report_form = ReportForm(report_data, report_files)
        self.assertTrue(report_form.is_valid(), f'report_form not valid: {report_form.errors}')

        response = self.client.post(reverse('report_article', args=[article.id]),
                                    data=report_data, multipart=True)

        self.assertRedirects(response, reverse('home'))
        reports = Report.objects.filter(description=report_data['description'])
        self.assertEqual(len(reports), 1)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        self.assertEqual(reports[0].status, ReportStatus.OPENED.n)
        self.assertEqual(reports[0].article.status, ArticleStatus.CHANGES_REQUESTED.n)

    def master_editor_assign_the_report(self, report_type):
        """ Assign the report to the editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[4]['username'], 'password': USERS[4]['password']})
        self.assertRedirects(response, reverse('home'))

        old_report = None
        if report_type == 'new':
            old_report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            old_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        self.assertFalse(old_report.editor)

        assign_data = {
            'report_id': old_report.id,
            'editor_assign_id': User.objects.get(username=USERS[2]['username']).id,
        }

        response = self.client.post(reverse('manage_report', args=[old_report.id]), data=assign_data)
        self.assertRedirects(response, reverse('home'))

        report = None
        if report_type == 'new':
            report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        self.assertEqual(report.editor.username, USERS[2]['username'])

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        if report_type == 'new':
            self.assertEqual(report.status, ReportStatus.NA_ASSIGNED.n)
            self.assertEqual(report.article.status, ArticleStatus.UNAPPROVED.n)
        elif report_type == 'open':
            self.assertEqual(report.status, ReportStatus.ASSIGNED.n)
            self.assertEqual(report.article.status, ArticleStatus.CHANGES_REQUESTED.n)

    def editor_editing_article(self, report_type):
        """ Edit article by assigned editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
        self.assertRedirects(response, reverse('home'))

        report = None
        if report_type == 'new':
            report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        article = Article.objects.get(id=report.article_id)

        edited_data = {
            'title': article.title,
            'tags': 'new_tag',
        }

        self.assertNotEquals(article.tags, edited_data['tags'])

        response = self.client.post(reverse('edit_article', args=[article.id]), data=edited_data)
        self.assertRedirects(response, reverse('home'))

        edited_article = Article.objects.get(id=report.article_id)
        self.assertEqual(list(edited_article.tags.values_list('name', flat=True)), edited_data['tags'].split(', '))

        edited_report = None
        if report_type == 'new':
            edited_report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            edited_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        if report_type == 'new':
            self.assertEqual(edited_report.status, ReportStatus.NA_CHANGES_APPLIED.n)
        elif report_type == 'open':
            self.assertEqual(edited_report.status, ReportStatus.CHANGES_APPLIED.n)

        self.assertEqual(report.article.status, ArticleStatus.CHANGES_DURING_REPORT.n)

    def editor_closes_report(self, report_type):
        """ Close the report by editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
        self.assertRedirects(response, reverse('home'))

        old_report = None
        if report_type == 'new':
            old_report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            old_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        close_report_data = {
            'close_report': 'Close Report',
        }

        response = self.client.post(reverse('manage_report', args=[old_report.id]), data=close_report_data)
        self.assertRedirects(response, reverse('home'))

        report = None
        if report_type == 'new':
            report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        if report_type == 'new':
            if (old_report.status == ReportStatus.NA_CHANGES_APPLIED.n or
                    old_report.status == ReportStatus.NA_ASSIGNED.n):
                self.assertEqual(report.status, ReportStatus.CONCLUDED.n)
            else:
                raise ValueError(f'unexpected report status: {ReportStatus.get_status_name(old_report.status)}')
        elif report_type == 'open':
            if old_report.status == ReportStatus.CHANGES_APPLIED.n:
                self.assertEqual(report.status, ReportStatus.CONCLUDED.n)
            elif old_report.status == ReportStatus.ASSIGNED.n:
                self.assertEqual(report.status, ReportStatus.REJECTED.n)
            else:
                raise ValueError(f'unexpected report status: {ReportStatus.get_status_name(old_report.status)}')

        self.assertEqual(report.article.status, ArticleStatus.APPROVED.n)

    def editor_rejects_report(self, report_type):
        """ Close the report by editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
        self.assertRedirects(response, reverse('home'))

        old_report = None
        if report_type == 'new':
            old_report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            old_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        reject_article_data = {
            'reject_article': 'Reject Article',
        }

        response = self.client.post(reverse('manage_report', args=[old_report.id]), data=reject_article_data)
        self.assertRedirects(response, reverse('home'))

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

        report = None
        if report_type == 'new':
            report = Report.objects.get(description=f'Review new article "{FORM_DATA["title"]}"')
        elif report_type == 'open':
            report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        self.assertEqual(report.status, ReportStatus.ARTICLE_REJECTED.n)
        self.assertEqual(report.article.status, ReportStatus.REJECTED.n)

    @parameterized.expand(['reject', 'edit reject', 'close', 'edit close'])
    def test_statuses_new_article(self, editor_behavior):
        self.user_create_article()
        self.master_editor_assign_the_report('new')
        if 'edit' in editor_behavior:
            self.editor_editing_article('new')

        if 'close' in editor_behavior:
            self.editor_closes_report('new')
        elif 'reject' in editor_behavior:
            self.editor_rejects_report('new')

    @parameterized.expand(['reject', 'edit reject', 'close', 'edit close'])
    def tests_statuses_report_existing_article(self, editor_behavior):
        Article.objects.create(
            title=FORM_DATA['title'],
            author=self.test_users['users'][0],
            created_at=datetime.today().strftime('%Y-%m-%d'),
            tags=FORM_DATA['tags'],
            status=ArticleStatus.APPROVED.n,
        )
        self.user_report_article()
        self.master_editor_assign_the_report('open')

        if 'edit' in editor_behavior:
            self.editor_editing_article('open')

        if 'close' in editor_behavior:
            self.editor_closes_report('open')
        elif 'reject' in editor_behavior:
            self.editor_rejects_report('open')

from datetime import datetime
from django.test import TestCase, Client

from django.contrib.auth.models import Group, User
from django.urls import reverse
from parameterized import parameterized

from editor_app.models import Report
from tests.MainTestBase import MainTestBase, FORM_DATA
from user_app.forms import StepFormSetCreate
from user_app.models import Article, Step

# Create your tests here.


class AccessTestsBase(MainTestBase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.user = None

    def get_home_page_contents(self):
        """ generate lists of contents for navbar, footer and home page """

        navbar_elements = [
            '<a class="nav-link" href="/user_app/home">Home',
            '<a class="nav-link" href="/user_app/search">Search',
            '<a class="nav-link" href="/user_app/create_article">Create article</a>',
            '<a class="nav-link" href="/user_app/user_panel">User Panel',
            '<a class="nav-link" href="/editor_app/editor_panel">Editor Panel',
            '<a class="nav-link" href="/editor_app/master_editor_panel">Master Editor Panel',
            '<a class="nav-link" href="/registration/logout">Logout',
        ]
        footer_elements = [
            '<div>Community Helpdesk Service</div>',
            '<div>Author: Radosław Relidzyński</div>',
            '<div>&copy; 2023</div>',
        ]
        home_elements = [
            'Search articles',
            'Create new article',
            'Go to user panel',
            'Go to editor panel',
            'Go to master editor panel',
        ]

        if not self.user:
            navbar_elements.remove(
                '<a class="nav-link" href="/user_app/create_article">Create article</a>')
            navbar_elements.remove('<a class="nav-link" href="/user_app/user_panel">User Panel')
            navbar_elements.remove(
                '<a class="nav-link" href="/editor_app/editor_panel">Editor Panel')
            navbar_elements.remove(
                '<a class="nav-link" href="/editor_app/master_editor_panel">Master Editor Panel')
            navbar_elements.remove('<a class="nav-link" href="/registration/logout">Logout')
            navbar_elements.append('<a class="nav-link" href="/registration/register">Register')
            navbar_elements.append('<a class="nav-link" href="/registration/login">Login')
            home_elements.remove('Create new article')
            home_elements.remove('Go to user panel')
            home_elements.remove('Go to editor panel')
            home_elements.remove('Go to master editor panel')
            return navbar_elements, footer_elements, home_elements

        if not self.user.groups.values_list('name', flat=True).filter(name='MasterEditors'):
            navbar_elements.remove(
                '<a class="nav-link" href="/editor_app/master_editor_panel">Master Editor Panel')
            home_elements.remove('Go to master editor panel')

            if not self.user.groups.values_list('name', flat=True).filter(name='Editors'):
                navbar_elements.remove(
                    '<a class="nav-link" href="/editor_app/editor_panel">Editor Panel')
                home_elements.remove('Go to editor panel')

        return navbar_elements, footer_elements, home_elements

    def test_base_template_and_home_page_access_and_content(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        navbar_elements, footer_elements, home_elements = self.get_home_page_contents()

        self.assertContains(response, '<li class="nav-item active">', count=len(navbar_elements))
        self.assertContains(response, '<li class="nav-item active">', count=len(navbar_elements))

        for element in navbar_elements:
            self.assertContains(response, element, count=1)

        self.assertContains(response, '<footer class="card-footer text-body-secondary '
                                      'fixed-bottom d-flex justify-content-between bg-dark">', count=1)

        for element in footer_elements:
            self.assertContains(response, element, count=1)

        for element in home_elements:
            self.assertContains(response, element, count=1)

    def test_search_page_access_and_content(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Search by Title', count=2)
        self.assertContains(response, 'Search by Tags', count=2)

        if self.client.session.get('_auth_user_id'):
            self.assertContains(response, 'Search by Ownership', count=1)
        else:
            self.assertNotContains(response, 'Search by Ownership')

    def test_search_page_searching_by_title(self):
        response = self.client.post(reverse('search'),
                                    {'search_title': 'Test Article', 'search_by_title': 'Search by Title'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h3>Search Results:</h3>")
        count_articles = Article.objects.filter(title__contains='Test Article').count()
        self.assertContains(response, 'Test Article', count=count_articles)
        self.assertContains(response, '<button type="submit" name="view_article"', count=count_articles)

    @parameterized.expand(['tag2', 'tag0', 'tag1', 'tag2, tag0', 'tag2, tag1', 'tag3'])
    def test_search_page_searching_by_tags(self, tags_to_search):
        response = self.client.post(reverse('search'),
                                    {'search_tags': tags_to_search, 'search_by_tags': 'Search by Tags'})
        self.assertEqual(response.status_code, 200)

        if len(Article.objects.filter(tags__name__in=tags_to_search.split(', '))) > 0:
            self.assertContains(response, "Search Results:")

        for article in Article.objects.filter(tags__name__in=tags_to_search.split(', ')):
            self.assertContains(response, article.title)

    def test_search_page_searching_by_ownership(self):
        response = self.client.post(reverse('search'), {'search_by_ownership': 'Search by Ownership'})

        if self.client.session.get('_auth_user_id'):
            self.assertEqual(response.status_code, 200)
            user_articles = Article.objects.filter(author_id=self.client.session.get('_auth_user_id'))
            if len(user_articles) > 0:
                self.assertContains(response, "Search Results:")
                self.assertContains(response, '<button type="submit" name="view_article"',
                                    count=len(user_articles))
            for user_article in user_articles:
                self.assertContains(response, user_article.title)
        else:
            self.assertEqual(response.status_code, 401)

    def test_view_article_page_access_and_content(self):
        articles = Article.objects.all()
        for article in articles:
            response = self.client.get(reverse('view_article', args=[article.id]))
            self.assertEqual(response.status_code, 200)

            if self.client.session.get('_auth_user_id'):
                self.assertContains(response, '<button type="submit" name="report_article">Report</button>', count=1)

                if article.author_id == int(self.client.session.get('_auth_user_id')):
                    self.assertContains(response, '<button type="submit" name="edit_article">Edit</button>', count=1)
                else:
                    self.assertNotContains(response, '<button type="submit" name="edit_article">Edit</button>')
            else:
                self.assertNotContains(response, '<button type="submit" name="report_article">Report</button>')
                self.assertNotContains(response, '<button type="submit" name="edit_article">Edit</button>')

    def test_edit_article_page_access_and_content(self):
        articles = Article.objects.all()
        for article in articles:
            response = self.client.get(reverse('edit_article', args=[article.id]))
            if self.client.session.get('_auth_user_id'):
                if article.author_id == int(self.client.session.get('_auth_user_id')):
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, article.title)
                else:
                    self.assertRedirects(response, reverse('home'))
            else:
                self.assertRedirects(response, reverse('login') + "?next=" + reverse('edit_article', args=[article.id]))

    def test_create_article_page_access_and_content(self):
        response = self.client.get(reverse('create_article'))

        if self.client.session.get('_auth_user_id'):
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<form action="#" method="post" class="form-group" '
                                          'id="article-form" enctype="multipart/form-data">')

            initial_article_count = Article.objects.count()
            initial_step_count = Step.objects.count()

            step_form_set = StepFormSetCreate(FORM_DATA)
            self.assertTrue(step_form_set.is_valid(), f"step_form_set not valid: {step_form_set.errors}")

            response = self.client.post(reverse('create_article'), data=FORM_DATA)

            self.assertRedirects(response, reverse('home'))

            self.assertEqual(Article.objects.count(), initial_article_count + 1)
            self.assertEqual(Article.objects.latest('id').title, FORM_DATA['title'])
            self.assertEqual(Article.objects.latest('id').tags.count(), len(FORM_DATA['tags'].split(",")))

            self.assertEqual(Step.objects.count(), initial_step_count + 2)
            self.assertEqual(
                Step.objects.get(title=FORM_DATA['form-0-title']).description1, FORM_DATA['form-0-description1'])
            self.assertEqual(
                Step.objects.get(title=FORM_DATA['form-1-title']).description1, FORM_DATA['form-1-description1'])


        else:
            self.assertRedirects(response, reverse('login') + "?next=" + reverse('create_article'))

    def test_user_panel_page_access_and_content(self):
        response = self.client.get(reverse('user_panel'))
        if self.client.session.get('_auth_user_id'):
            self.assertEqual(response.status_code, 200)

            user_id = int(self.client.session.get('_auth_user_id'))

            user_articles = Article.objects.filter(author_id=user_id)
            if len(user_articles) > 0:
                self.assertContains(response, '<h3>Your Articles:</h3>')
                for article in user_articles:
                    self.assertContains(response, article.title)
            else:
                self.assertContains(response, "<p>You haven't authored any articles yet.</p>")

            other_articles = Article.objects.exclude(author_id=user_id)
            for article in other_articles:
                self.assertNotContains(response, article.title)

            user_reports = Report.objects.filter(author_id=user_id)
            if len(user_reports) > 0:
                for report in user_reports:
                    self.assertContains(response, '<h3>Your Reports:</h3>')
                    self.assertContains(response, report.title)
            else:
                self.assertContains(response, "<p>You haven't authored any reports yet.</p>")

            other_reports = Report.objects.exclude(author_id=user_id)
            for report in other_reports:
                self.assertNotContains(response, report.title)

        else:
            self.assertRedirects(response, reverse('login') + "?next=" + reverse('user_panel'))

    def test_report_article_page_access_and_content(self):
        articles = Article.objects.all()
        for article in articles:
            response = self.client.get(reverse('report_article', args=[article.id]))

            if self.client.session.get('_auth_user_id'):
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "<h1><span>Report Article</span></h1>")
                self.assertContains(response, article.title)
            else:
                self.assertRedirects(response,
                                     reverse('login') + "?next=" + reverse('report_article', args=[article.id]))

    def test_view_report_page_access_and_content(self):
        reports = Report.objects.all()
        for report in reports:
            response = self.client.get(reverse('view_report', args=[report.id]))

            if self.client.session.get('_auth_user_id'):
                if report.author_id == self.client.session.get('_auth_user_id'):
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "<h1>View Report Page</h1>")
                    self.assertContains(response, report.title)
                else:
                    self.assertRedirects(response, reverse('home'))
            else:
                self.assertRedirects(response,
                                     reverse('login') + "?next=" + reverse('view_report', args=[report.id]))

    def test_editor_panel_page_access_and_content(self):
        response = self.client.get(reverse('editor_panel'))

        if self.client.session.get('_auth_user_id'):
            user_id = int(self.client.session.get('_auth_user_id'))

            editor = User.objects.get(id=user_id)

            if editor.groups.values_list('name', flat=True).filter(name='Editors'):
                self.assertEqual(response.status_code, 200)

                editor_reports = Report.objects.filter(editor=editor)
                if len(editor_reports) > 0:
                    self.assertContains(response, '<h3>Your Reports to resolve:</h3>')
                    for report in editor_reports:
                        self.assertContains(response, report.title)
                else:
                    self.assertContains(response, "<p>You have no reports assigned for now</p>")

            else:
                self.assertRedirects(response, reverse('home'))

    def test_master_editor_panel_page_access_and_content(self):
        response = self.client.get(reverse('master_editor_panel'))

        if self.client.session.get('_auth_user_id'):
            user_id = int(self.client.session.get('_auth_user_id'))

            editor = User.objects.get(id=user_id)

            if editor.groups.values_list('name', flat=True).filter(name='MasterEditors'):
                self.assertEqual(response.status_code, 200)

                editor_reports = Report.objects.filter(editor=editor)
                if len(editor_reports) > 0:
                    self.assertContains(response, '<h3>Existing reports</h3>')
                    for report in editor_reports:
                        self.assertContains(response, report.title)
                else:
                    self.assertContains(response, "<p>There are no reports to manage</p>")

            else:
                self.assertRedirects(response, reverse('home'))

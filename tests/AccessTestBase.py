from datetime import datetime
from django.test import TestCase, Client

from django.contrib.auth.models import Group, User
from django.urls import reverse
from parameterized import parameterized

from editor_app.models import Report
from user_app.forms import ArticleForm
from user_app.models import Article

# Create your tests here.


USERS = [
    {'username': 'test_user1', 'password': 'user_password1', 'number_of_articles': 5},
    {'username': 'test_user2', 'password': 'user_password2', 'number_of_articles': 5},
    {'username': 'test_editor1', 'password': 'editor_password1'},
    {'username': 'test_editor2', 'password': 'editor_password2'},
    {'username': 'test_master_editor1', 'password': 'master_editor_password1'},
]


class AccessTestsBase(TestCase):
    test_users = {
        'users': [],
        'editors': [],
        'master_editors': [],
    }

    @classmethod
    def setUpTestData(cls):
        """ setUp separate database to test functionalities """
        editors_group, created = Group.objects.get_or_create(name='Editors')
        master_editors_group, created = Group.objects.get_or_create(name='MasterEditors')

        for user in USERS:
            test_user = User.objects.create_user(username=user['username'], password=user['password'])

            if 'editor' in test_user.username:
                test_user.groups.add(editors_group)
                cls.test_users['editors'].append(test_user)
                if 'master' in test_user.username:
                    test_user.groups.add(master_editors_group)
                    cls.test_users['master_editors'].append(test_user)
            else:
                cls.test_users['users'].append(test_user)

            if 'number_of_articles' in user:
                for i in range(user['number_of_articles']):
                    Article.objects.create(
                        title=f'Test Article {user["username"]}-{i}',
                        author=test_user,
                        created_at=datetime.today().strftime('%Y-%m-%d'),
                        tags=f'tag2, tag{i % 2}'
                    )

    def setUp(self):
        """setUp method for AccessTests"""
        self.client = Client()

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.logout()
    def get_home_page_contents(self):
        """ generate lists of contents for navbar, footer and home page """

        navbar_elements = [
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/home">Home',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/search">Search',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/user_panel">User Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/editor_panel">Editor Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/master_editor_panel">Master Editor Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/registration/logout">Logout',
        ]
        footer_elements = [
            '<div class="footer-left">Community Helpdesk Service</div>',
            '<div class="footer-center">Author: Radosław Relidzyński</div>',
            '<div class="footer-right">&copy; 2023</div>',
        ]
        home_elements = [
            '<h5>Search articles <a href="/user_app/search">HERE</a></h5>',
            '<h5>Create article <a href="/user_app/create_article">HERE</a></h5>',
            '<h5>Go to user panel <a href="/user_app/user_panel">HERE</a></h5>',
            '<h5>Go to editor panel <a href="/editor_app/editor_panel">HERE</a></h5>',
            '<h5>Go to master editor panel <a href="/editor_app/master_editor_panel">HERE</a></h5>',
        ]

        try:
            user = User.objects.get(id=self.client.session.get('_auth_user_id'))
        except User.DoesNotExist:
            navbar_elements.remove('<a class="nav-link" href="http://127.0.0.1:8000/user_app/user_panel">User Panel')
            navbar_elements.remove(
                '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/editor_panel">Editor Panel')
            navbar_elements.remove(
                '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/master_editor_panel">Master Editor Panel')
            navbar_elements.remove('<a class="nav-link" href="http://127.0.0.1:8000/registration/logout">Logout')
            navbar_elements.append('<a class="nav-link" href="http://127.0.0.1:8000/registration/register">Register')
            navbar_elements.append('<a class="nav-link" href="http://127.0.0.1:8000/registration/login">Login')
            home_elements.remove('<h5>Create article <a href="/user_app/create_article">HERE</a></h5>')
            home_elements.remove('<h5>Go to user panel <a href="/user_app/user_panel">HERE</a></h5>')
            home_elements.remove('<h5>Go to editor panel <a href="/editor_app/editor_panel">HERE</a></h5>')
            home_elements.remove(
                '<h5>Go to master editor panel <a href="/editor_app/master_editor_panel">HERE</a></h5>')
            return navbar_elements, footer_elements, home_elements

        if not user.groups.values_list('name', flat=True).filter(name='MasterEditors'):
            navbar_elements.remove(
                '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/editor_panel">Editor Panel')
            home_elements.remove('<h5>Go to editor panel <a href="/editor_app/editor_panel">HERE</a></h5>')

            if not user.groups.values_list('name', flat=True).filter(name='Editors'):
                navbar_elements.remove(
                    '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/master_editor_panel">'
                    'Master Editor Panel')
                home_elements.remove(
                    '<h5>Go to master editor panel <a href="/editor_app/master_editor_panel">HERE</a></h5>')

        return navbar_elements, footer_elements, home_elements

    def test_base_template_and_home_page_access_and_content(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        navbar_elements, footer_elements, home_elements = self.get_home_page_contents()

        self.assertContains(response, '<li class="nav-item active">', count=len(navbar_elements))
        for element in navbar_elements:
            self.assertContains(response, element, count=1)

        self.assertContains(response, '<footer class="footer text-center">', count=1)
        for element in footer_elements:
            self.assertContains(response, element, count=1)

        for element in home_elements:
            self.assertContains(response, element, count=1)

    def test_search_page_access_and_content(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, '<button type="submit" name="search_title">Search by Title</button>', count=1)
        self.assertContains(response, '<button type="submit" name="search_tags">Search by Tags</button>', count=1)

        if self.client.session.get('_auth_user_id'):
            self.assertContains(response, '<button type="submit" name="search_ownership">Search by Ownership</button>',
                                count=1)

    def test_search_page_searching_by_title(self):
        response = self.client.post(reverse('search'),
                                    {'search_text': 'Test Article', 'search_title': 'Search by Title'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search Results:")
        count_articles = Article.objects.filter(title__contains='Test Article').count()
        self.assertContains(response, 'Test Article', count=count_articles)
        self.assertContains(response, '<button type="submit" name="view_article">View</button>', count=count_articles)

    @parameterized.expand(['tag2', 'tag0', 'tag1', 'tag2, tag0', 'tag2, tag1', 'tag3'])
    def test_search_page_searching_by_tags(self, tags_to_search):
        response = self.client.post(reverse('search'),
                                    {'tags': tags_to_search, 'search_tags': 'Search by Tags'})
        self.assertEqual(response.status_code, 200)

        if len(Article.objects.filter(tags__name__in=tags_to_search.split(', '))) > 0:
            self.assertContains(response, "Search Results:")

        for article in Article.objects.filter(tags__name__in=tags_to_search.split(', ')):
            self.assertContains(response, article.title)

    def test_search_page_searching_by_ownership(self):
        response = self.client.post(reverse('search'), {'search_ownership': 'Search by Ownership'})

        if self.client.session.get('_auth_user_id'):
            self.assertEqual(response.status_code, 200)
            user_articles = Article.objects.filter(author_id=self.client.session.get('_auth_user_id'))
            if len(user_articles) > 0:
                self.assertContains(response, "Search Results:")
                self.assertContains(response, '<button type="submit" name="view_article">View</button>',
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
            self.assertContains(response, '<form action="#" method="post" class="form-group">')

            form_data = {
                'title': 'New Test Article',
                'tags': 'tag1, tag2',
            }
            form = ArticleForm(data=form_data)
            self.assertTrue(form.is_valid())

            response = self.client.post(reverse('create_article'), form_data)
            self.assertRedirects(response, reverse('home'))

            new_article = Article.objects.get(title='New Test Article')
            self.assertEqual(new_article.author_id, int(self.client.session.get('_auth_user_id')))
            self.assertEqual(list(new_article.tags.names()), ['tag1', 'tag2'])

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
                self.assertContains(response, "<h1>Report Article page</h1>")
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


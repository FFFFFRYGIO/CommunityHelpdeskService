from django.test import TestCase, Client
from registration.models import User
from .forms import ArticleForm
from .models import Article
from django.urls import reverse
from parameterized import parameterized
from django.contrib.auth.models import Group
from datetime import datetime


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
        self.navbar_elements = []
        self.footer_elements = [
            '<div class="footer-left">Community Helpdesk Service</div>',
            '<div class="footer-center">Author: Radosław Relidzyński</div>',
            '<div class="footer-right">&copy; 2023</div>',
        ]
        self.home_elements = []

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.post(reverse('logout'))

    def test_base_template_access_and_content(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, '<li class="nav-item active">', count=len(self.navbar_elements))
        for element in self.navbar_elements:
            self.assertContains(response, element, count=1)

        self.assertContains(response, '<footer class="footer text-center">', count=1)
        for element in self.footer_elements:
            self.assertContains(response, element, count=1)

    def test_home_page_access_and_content(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        for element in self.home_elements:
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
        article_ids = Article.objects.values_list('id', flat=True)
        for article_id in article_ids:
            response = self.client.get(reverse('view_article', args=[article_id]))
            self.assertEqual(response.status_code, 200)

            if self.client.session.get('_auth_user_id'):
                self.assertContains(response, '<button type="submit" name="report_article">Report</button>', count=1)

                if Article.objects.get(id=article_id).author.id == int(self.client.session.get('_auth_user_id')):
                    self.assertContains(response, '<button type="submit" name="edit_article">Edit</button>', count=1)
                else:
                    self.assertNotContains(response, '<button type="submit" name="edit_article">Edit</button>')
            else:
                self.assertNotContains(response, '<button type="submit" name="report_article">Report</button>')
                self.assertNotContains(response, '<button type="submit" name="edit_article">Edit</button>')



class UnauthenticatedUserAccessTests(AccessTestsBase):

    def setUp(self):
        super().setUp()
        unauthenticated_user_navbar_elements = [
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/home">Home',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/search">Search',
            '<a class="nav-link" href="http://127.0.0.1:8000/registration/register">Register',
            '<a class="nav-link" href="http://127.0.0.1:8000/registration/login">Login',
        ]
        self.navbar_elements = unauthenticated_user_navbar_elements
        unauthenticated_user_home_elements = [
            '<h5>Search articles <a href="/user_app/search">HERE</a></h5>'
        ]
        self.home_elements = unauthenticated_user_home_elements


class AuthenticatedUserAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['users'][0])

        authenticated_user_navbar_elements = [
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/home">Home',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/search">Search',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/user_panel">User Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/registration/logout">Logout',
        ]
        self.navbar_elements = authenticated_user_navbar_elements


class EditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['editors'][0])

        editor_navbar_elements = [
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/home">Home',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/search">Search',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/user_panel">User Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/editor_panel">Editor Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/registration/logout">Logout',
        ]
        self.navbar_elements = editor_navbar_elements


class MasterEditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['editors'][0])

        master_editor_navbar_elements = [
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/home">Home',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/search">Search',
            '<a class="nav-link" href="http://127.0.0.1:8000/user_app/user_panel">User Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/editor_panel">Editor Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/editor_app/master_editor_panel">Master Editor Panel',
            '<a class="nav-link" href="http://127.0.0.1:8000/registration/logout">Logout',
        ]
        self.navbar_elements = master_editor_navbar_elements


class OldAllUsersAccessTests(AccessTestsBase):
    def test_home_page_access(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search articles")

    def test_search_page_access(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search by name")
        self.assertContains(response, "Search by tags")

    def test_search_page_searching_by_name(self):
        response = self.client.post(reverse('search'),
                                    {'search_text': 'Test Article', 'search_title': 'Search by Title'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search Results:")
        self.assertContains(response, "Test Article",
                            count=len(self.ids_of_owned_articles) + len(self.ids_of_not_owned_articles))

        for article_id in self.ids_of_owned_articles:
            response = self.client.post(reverse('search'),
                                        {'search_text': f'Test Article {article_id}', 'search_title': 'Search by Title'})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Search Results:")
            self.assertContains(response, f"Test Article {article_id}", count=1)

    @parameterized.expand(['tag2', 'tag0', 'tag1', 'tag2, tag0', 'tag2, tag1', 'tag3'])
    def test_search_page_searching_by_tags(self, tags_to_search):
        response = self.client.post(reverse('search'),
                                    {'tags': tags_to_search, 'search_tags': 'Search by Tags'})
        self.assertEqual(response.status_code, 200)

        if len(Article.objects.filter(tags__name__in=tags_to_search.split(', '))) > 0:
            self.assertContains(response, "Search Results:")

        for article in Article.objects.filter(tags__name__in=tags_to_search.split(', ')):
            self.assertContains(response, article.title)

    def test_non_existent_page_access(self):
        response = self.client.get('/nonExistentPage/')
        self.assertEqual(response.status_code, 404)


class OldUnauthenticatedUserAccessTests(AccessTestsBase):

    def test_home_page_access(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Create article")
        self.assertNotContains(response, "Go to user panel")

    def test_search_page_access(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Search by recently viewed")

    def test_search_page_searching_by_ownership(self):
        response = self.client.post(reverse('search'),
                                    {'search_ownership': 'Search by Ownership'})
        self.assertEqual(response.status_code, 401)

    def test_view_article_page_access(self):
        for articles_ids_list in (self.ids_of_owned_articles, self.ids_of_not_owned_articles):
            for article_id in articles_ids_list:
                response = self.client.get(reverse('view_article', args=[article_id]))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'Edit')

    def test_create_article_page_access(self):
        response = self.client.get(reverse('create_article'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('create_article'))

    def test_edit_article_page_access(self):
        for articles_ids_list in (self.ids_of_owned_articles, self.ids_of_not_owned_articles):
            for article_id in articles_ids_list:
                response = self.client.get(reverse('edit_article', args=[article_id]))
                self.assertRedirects(response, reverse('login') + "?next=" + reverse('edit_article', args=[article_id]))

    def test_create_report_page_access(self):
        for articles_ids_list in (self.ids_of_owned_articles, self.ids_of_not_owned_articles):
            for article_id in articles_ids_list:
                response = self.client.get(reverse('create_report', args=[article_id]))
                self.assertRedirects(response, reverse('login') + "?next=" + reverse('create_report', args=[article_id]))

    def test_user_panel_page_access(self):
        response = self.client.get(reverse('user_panel'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('user_panel'))


class OldAuthenticatedUserAccessTests(AccessTestsBase):

    def setUp(self):
        """setUp class for AuthenticatedUserAccessTests"""
        super().setUp()
        self.client.force_login(self.test_users[0])

    def test_home_page_access(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create article")
        self.assertContains(response, "Go to user panel")

    def test_search_page_access(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search by ownership")

    def test_search_page_searching_by_ownership(self):
        response = self.client.post(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search by ownership")

        response = self.client.post(reverse('search'),
                                    {'search_ownership': 'Search by Ownership'})

        self.assertContains(response, "Search Results:")
        self.assertContains(response, "Test Article", count=5)

        for article_id in self.ids_of_owned_articles:
            self.assertContains(response, f"Test Article {article_id}", count=1)

    def test_view_article_page_access(self):
        for articles_ids_list in (self.ids_of_owned_articles, self.ids_of_not_owned_articles):
            for article_id in articles_ids_list:
                response = self.client.get(reverse('view_article', args=[article_id]))
                self.assertEqual(response.status_code, 200)
                article = Article.objects.get(id=article_id)
                print(article_id, article.author, self.test_users[0])
                if article.author == self.test_users[0]:
                    self.assertContains(response, 'Edit', count=5)
                else:
                    self.assertContains(response, 'Edit', count=4)

    def test_create_article_page_access(self):
        response = self.client.get(reverse('create_article'))
        self.assertEqual(response.status_code, 200)
        form_data = {
            'title': 'New Test Article',
            'tags': 'tag1, tag2',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post(reverse('create_article'), form_data)
        self.assertEqual(response.status_code, 302)

        new_article = Article.objects.get(title='New Test Article')
        self.assertEqual(new_article.author, self.test_users[0])

        self.assertEqual(list(new_article.tags.names()), ['tag1', 'tag2'])

        self.assertRedirects(response, reverse('home'))

    def test_edit_article_page_access(self):
        for articles_ids_list in (self.ids_of_owned_articles, self.ids_of_not_owned_articles):
            for article_id in articles_ids_list:
                print(article_id)
                response = self.client.get(reverse('edit_article', args=[article_id]))
                article = Article.objects.get(id=article_id)
                if article.author == self.test_users[0]:
                    self.assertEqual(response.status_code, 200)
                else:
                    self.assertRedirects(response, reverse('home'))

    def test_edit_article_page_edit_owned(self):
        pass

    def test_create_report_page_access(self):
        for articles_ids_list in (self.ids_of_owned_articles, self.ids_of_not_owned_articles):
            for article_id in articles_ids_list:
                response = self.client.get(reverse('create_report', args=[article_id]))
                self.assertEqual(response.status_code, 200)
                # TODO: create report

    def test_user_panel_page_access(self):
        response = self.client.get(reverse('user_panel'))
        self.assertEqual(response.status_code, 200)
        # TODO: create reports and articles to check if they are seen here


del AccessTestsBase
del OldAllUsersAccessTests
del OldUnauthenticatedUserAccessTests
del OldAuthenticatedUserAccessTests

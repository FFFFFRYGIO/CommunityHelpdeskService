from django.test import TestCase, Client
from registration.models import User
from .forms import ArticleForm
from .models import Article
from django.urls import reverse
from parameterized import parameterized


# Create your tests here.

class AccessTestsBase(TestCase):
    number_of_articles = 5
    test_user = None

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        for article_id in range(cls.number_of_articles):
            Article.objects.create(
                title=f'Test Article {article_id}',
                author=cls.test_user,
                created_at='2023-10-01',
                tags=f'tag2, tag{article_id % 2}'
            )

    def setUp(self):
        """setUp class for AccessTests"""
        self.client = Client()


class AllUsersAccessTests(AccessTestsBase):
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
                                    {'search_text': 'Test Article', 'search_name': 'Search by Name'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search Results:")
        self.assertContains(response, "Test Article", count=5)

        for article_id in range(self.number_of_articles):
            response = self.client.post(reverse('search'),
                                        {'search_text': f'Test Article {article_id}', 'search_name': 'Search by Name'})
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
        response = self.client.get('/nonexistentpage/')
        self.assertEqual(response.status_code, 404)


class UnauthenticatedUserAccessTests(AccessTestsBase):

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


    def test_create_article_page_access(self):
        response = self.client.get(reverse('create_article'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('create_article'))

    def test_edit_article_page_access(self):
        response = self.client.get(reverse('edit_article'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('edit_article'))

    def test_create_report_page_access(self):
        response = self.client.get(reverse('create_report'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('create_report'))

    def test_user_panel_page_access(self):
        response = self.client.get(reverse('user_panel'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('user_panel'))


class AuthenticatedUserAccessTests(AccessTestsBase):
    test_user = None

    def setUp(self):
        """setUp class for AuthenticatedUserAccessTests"""
        super().setUp()
        self.client.force_login(self.test_user)

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

        for article_id in range(self.number_of_articles):
            self.assertContains(response, f"Test Article {article_id}", count=1)

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
        self.assertEqual(new_article.author, self.test_user)

        self.assertEqual(list(new_article.tags.names()), ['tag1', 'tag2'])

        self.assertRedirects(response, reverse('home'))

    def test_edit_article_page_owned_article(self):
        response = self.client.get(reverse('edit_article'))
        self.assertEqual(response.status_code, 200)
        # TODO: edit owned article

    def test_edit_article_page_not_owned_article(self):
        response = self.client.get(reverse('edit_article'))
        self.assertEqual(response.status_code, 9999)
        # TODO: edit not owned article

    def test_create_report_page_access(self):
        response = self.client.get(reverse('create_report'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('create_report'))
        # TODO: create report

    def test_user_panel_page_access(self):
        response = self.client.get(reverse('user_panel'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('user_panel'))
        # TODO: create reports and articles to check if they are seen here

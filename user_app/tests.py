from django.test import TestCase, Client
from registration.models import User
from .forms import ArticleForm
from .models import Article
from django.urls import reverse
from parameterized import parameterized


# Create your tests here.

class AccessTestsBase(TestCase):
    ids_of_owned_articles = list(range(1, 6))
    ids_of_not_owned_articles = list(range(6, 9))
    test_users = [None, None]

    @classmethod
    def setUpTestData(cls):
        cls.test_users[0] = User.objects.create_user(username='testUserOwner', password='test_password')
        cls.test_users[1] = User.objects.create_user(username='testUserNotOwner', password='test_password')
        for article_id in cls.ids_of_owned_articles:
            Article.objects.create(
                title=f'Test Article {article_id}',
                author=cls.test_users[0],
                created_at='2023-10-01',
                tags=f'tag2, tag{article_id % 2}'
            )

        for article_id in cls.ids_of_not_owned_articles:
            Article.objects.create(
                title=f'Test Article {article_id}',
                author=cls.test_users[1],
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
        self.assertContains(response, "Test Article",
                            count=len(self.ids_of_owned_articles) + len(self.ids_of_not_owned_articles))

        for article_id in self.ids_of_owned_articles:
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
        response = self.client.get('/nonExistentPage/')
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


class AuthenticatedUserAccessTests(AccessTestsBase):

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

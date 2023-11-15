from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from user_app.forms import StepFormSetCreate
from user_app.models import Article, Step

# Create your tests here.


class ArticleTests(TestCase):
    user = None

    @classmethod
    def setUpTestData(cls):
        """ setUp separate database to test functionalities """
        User.objects.create_user(username='system_automat', password='system_password1')
        cls.user = User.objects.create_user(username='standart_user', password='user_password1')

        for i in range(1, 5):
            article = Article.objects.create(
                title=f"Test title {i}", author=cls.user,
                created_at=datetime.now(), tags="tag", status="opened")
            for j in range(i):
                Step.objects.create(
                    article=article, ordinal_number=j+1,
                    title=f"Step title {i}", description1=f"Step description1 {i}")

    def setUp(self):
        """setUp method for AccessTests"""
        self.client = Client()
        self.client.force_login(self.user)

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.logout()

    def test_edit_article_no_changes(self):
        for article in Article.objects.all():
            steps = Step.objects.filter(article=article).order_by('ordinal_number')
            form_data = {
                'title': article.title,
                'tags': "tag",
                'form-TOTAL_FORMS': str(steps.count()),
                'form-INITIAL_FORMS': str(steps.count()),
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
            }
            for i, step in enumerate(steps):
                form_data[f'form-{i}-id'] = step.id
                form_data[f'form-{i}-title'] = step.title
                form_data[f'form-{i}-ordinal_number'] = step.ordinal_number
                form_data[f'form-{i}-description1'] = step.description1

            step_form_set = StepFormSetCreate(form_data)
            self.assertTrue(step_form_set.is_valid(), f"step_form_set not valid: {step_form_set.errors}")

            response = self.client.post(reverse('edit_article', args=[article.id]), data=form_data)
            self.assertRedirects(response, reverse('home'))

            edited_article = Article.objects.get(id=article.id)
            self.assertEqual(article, edited_article)

            self.assertEqual(Step.objects.filter(article=article).count(), steps.count())
            for step in steps:
                self.assertEqual(step, Step.objects.get(id=step.id))

    def test_edit_article_different_steps_amount(self):
        pass

    def test_edit_article_remove_steps(self):
        pass

    def test_edit_article_add_steps(self):
        pass

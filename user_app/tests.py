from datetime import datetime
from django.test import TestCase, Client

from django.contrib.auth.models import Group, User
from django.urls import reverse
from parameterized import parameterized

from editor_app.models import Report
from user_app.forms import ArticleForm, StepFormSet
from user_app.models import Article, Step

# Create your tests here.


class StepTesting(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ setUp separate database to test functionalities """
        User.objects.create_user(username='test_user', password='user_password1')

    def setUp(self):
        """setUp method for AccessTests"""
        self.client = Client()
        self.client.force_login(User.objects.get(username='test_user'))

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.logout()

    def test_create_article_with_steps(self):
        initial_article_count = Article.objects.count()
        initial_step_count = Step.objects.count()

        response = self.client.get(reverse('create_article'))
        self.assertEqual(response.status_code, 200)

        step_data = {
            'title': 'Test Article',
            'tags': 'tag1, tag2',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-title': 'Step 1',
            'form-0-description1': 'Description for Step 1',
            'form-1-title': 'Step 2',
            'form-1-description1': 'Description for Step 2',
        }

        step_form_set = StepFormSet(step_data)

        if not step_form_set.is_valid():
            print(step_form_set.errors)

        self.assertTrue(step_form_set.is_valid())

        response = self.client.post(reverse('create_article'), data=step_data)

        self.assertRedirects(response, reverse('home'))

        self.assertEqual(Article.objects.count(), initial_article_count + 1)
        self.assertEqual(Article.objects.latest('id').title, step_data['title'])
        self.assertEqual(Article.objects.latest('id').tags.count(), len(step_data['tags'].split(",")))

        # self.assertEqual(Step.objects.count(), initial_step_count + 2)
        self.assertEqual(Step.objects.get(title=step_data['form-0-title']).description1, step_data['form-0-description1'])
        self.assertEqual(Step.objects.get(title=step_data['form-1-title']).description1, step_data['form-1-description1'])

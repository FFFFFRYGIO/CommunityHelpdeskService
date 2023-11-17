from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from parameterized import parameterized

from user_app.forms import StepFormSetCreate
from user_app.models import Article, Step

# Create your tests here.


class ArticleTests(TestCase):
    user = None

    @classmethod
    def setUpTestData(cls):
        """ setUp separate database to test functionalities """
        User.objects.create_user(username='system_automat', password='system_password1')
        cls.user = User.objects.create_user(username='standard_user', password='user_password1')

        for i in range(1, 5):
            article = Article.objects.create(
                title=f"Test title {i}", author=cls.user,
                created_at=datetime.now(), tags="tag", status="opened")
            for j in range(i):
                Step.objects.create(
                    article=article, ordinal_number=j+1, title=f"Step {i} title",
                    description1=f"Step {i} description1", description2=f"Step {i} description2")

    def setUp(self):
        """setUp method for AccessTests"""
        self.client = Client()
        self.client.force_login(self.user)

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.logout()

    def generate_form_data(self, article, modify_content=True, modify_amount_number=0):
        """ returns form data based on parameters """
        steps = Step.objects.filter(article=article).order_by('ordinal_number')
        form_data = {
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            'form-TOTAL_FORMS': str(steps.count() + modify_amount_number),
            'form-INITIAL_FORMS': str(steps.count()),
        }
        if modify_content:
            form_data['title'] = article.title + " modified"
            form_data['tags'] = "tag" + " modified"
        else:
            form_data['title'] = article.title
            form_data['tags'] = "tag"

        for i in range(steps.count() + modify_amount_number):
            if i < steps.count():
                step = steps[i]
            else:
                step = Step(title=f"New step {i + 1} title", ordinal_number=i + 1,
                            description1=f"New step {i + 1} description1",
                            description2=f"New step {i + 1} description2")
                step.save()

            form_data[f'form-{i}-id'] = step.id
            form_data[f'form-{i}-ordinal_number'] = step.ordinal_number
            if modify_content:
                form_data[f'form-{i}-title'] = step.title + " modified"
                form_data[f'form-{i}-description1'] = step.description1 + " modified"
                form_data[f'form-{i}-description2'] = step.description2 + " modified"
            else:
                form_data[f'form-{i}-title'] = step.title
                form_data[f'form-{i}-description1'] = step.description1
                form_data[f'form-{i}-description2'] = step.description2

        step_form_set = StepFormSetCreate(form_data)
        self.assertTrue(step_form_set.is_valid(), f"step_form_set not valid: {step_form_set.errors}")

        return form_data

    def test_edit_article_no_changes(self):
        for article in Article.objects.all():
            steps_to_compare = [step.__dict__.copy() for step in Step.objects.filter(
                article=article).order_by('ordinal_number')]
            form_data = self.generate_form_data(article, modify_content=False)

            response = self.client.post(reverse('edit_article', args=[article.id]), data=form_data)
            self.assertRedirects(response, reverse('home'))

            edited_article = Article.objects.get(id=article.id)
            del article._state, edited_article._state
            self.assertEqual(article.__dict__, edited_article.__dict__)

            self.assertEqual(Step.objects.filter(article=article).count(), len(steps_to_compare))
            for step_dict in steps_to_compare:
                edited_step = Step.objects.get(id=step_dict['id'])
                self.assertNotEqual(step_dict, edited_step.__dict__)

                self.assertEqual(step_dict['title'], Step.objects.get(id=step_dict['id']).title)
                self.assertEqual(step_dict['description1'], Step.objects.get(id=step_dict['id']).description1)
                self.assertEqual(step_dict['description2'], Step.objects.get(id=step_dict['id']).description2)

    def test_edit_article_different_steps_amount(self):
        for article in Article.objects.all():
            steps_to_compare = [step.__dict__.copy() for step in Step.objects.filter(
                article=article).order_by('ordinal_number')]
            form_data = self.generate_form_data(article)

            response = self.client.post(reverse('edit_article', args=[article.id]), data=form_data)
            self.assertRedirects(response, reverse('home'))

            edited_article = Article.objects.get(id=article.id)
            del article._state, edited_article._state
            self.assertNotEqual(article.__dict__, edited_article.__dict__)

            self.assertEqual(article.title + " modified", edited_article.title)
            self.assertEqual(sorted(["tag", "modified"]), list(edited_article.tags.names()))

            self.assertEqual(Step.objects.filter(article=article).count(), len(steps_to_compare))
            for step_dict in steps_to_compare:
                edited_step = Step.objects.get(id=step_dict['id'])
                self.assertNotEqual(step_dict, edited_step.__dict__)

                self.assertEqual(step_dict['title'] + " modified", Step.objects.get(id=step_dict['id']).title)
                self.assertEqual(step_dict['description1'] + " modified", Step.objects.get(id=step_dict['id']).description1)
                self.assertEqual(step_dict['description2'] + " modified", Step.objects.get(id=step_dict['id']).description2)

    @parameterized.expand([-1, -2])
    def test_edit_article_remove_steps(self, modify_amount_number):
        pass

    @parameterized.expand([1, 2])
    def test_edit_article_add_steps(self):
        pass

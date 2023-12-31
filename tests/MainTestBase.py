from datetime import datetime

from django.contrib.auth.models import Group, User
from django.test import TestCase, Client

from user_app.models import Article

# Create your tests here.


USERS = [
    {'username': 'test_user1', 'password': 'user_password1', 'number_of_articles': 5},
    {'username': 'test_user2', 'password': 'user_password2', 'number_of_articles': 5},
    {'username': 'test_editor1', 'password': 'editor_password1'},
    {'username': 'test_editor2', 'password': 'editor_password2'},
    {'username': 'test_master_editor1', 'password': 'master_editor_password1'},
]

FORM_DATA = {
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


class MainTestBase(TestCase):
    test_users = {
        'users': [],
        'editors': [],
        'master_editors': [],
    }

    @classmethod
    def setUpTestData(cls):
        """ setUp separate database to test functionalities """
        User.objects.create_user(username='system_automat', password='system_password1')
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
                        tags=f'tag2, tag{i % 2}',
                        status='approved',
                    )

    def setUp(self):
        """setUp method for AccessTests"""
        self.client = Client()

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.logout()

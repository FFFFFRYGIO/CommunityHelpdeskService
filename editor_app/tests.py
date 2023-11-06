from django.test import TestCase, Client

from editor_app.models import Report
from registration.models import User
from .models import Article
from django.urls import reverse
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

    def tearDown(self):
        """tearDown method for AccessTestsBase"""
        self.client.logout()

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


class UnauthenticatedUserAccessTests(AccessTestsBase):
    pass


class AuthenticatedUserAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['users'][0])


class EditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['editors'][0])


class MasterEditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['master_editors'][0])


del AccessTestsBase

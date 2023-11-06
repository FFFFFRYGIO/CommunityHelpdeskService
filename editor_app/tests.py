from editor_app.models import Report
from registration.models import User
from django.urls import reverse

from tests.main_test_classes import AccessTestsBaseConfig


# Create your tests here.


class AccessTestsBase(AccessTestsBaseConfig):
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

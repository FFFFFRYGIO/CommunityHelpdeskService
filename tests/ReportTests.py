from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from editor_app.forms import ReportForm
from editor_app.models import Report
from tests.AccessTestBase import AccessTestsBase, USERS, FORM_DATA
from user_app.forms import StepFormSetCreate
from user_app.models import Article, Step


# Create your tests here.


class ReportsTests(AccessTestsBase):
    def user_create_article(self):
        """ Create article to be reported"""
        self.client.login(username=USERS[0]['username'], password=USERS[0]['password'])

        step_form_set = StepFormSetCreate(FORM_DATA)
        self.assertTrue(step_form_set.is_valid(), f"step_form_set not valid: {step_form_set.errors}")
        response = self.client.post(reverse('create_article'), data=FORM_DATA)

        self.assertRedirects(response, reverse('home'))
        articles = Article.objects.filter(title=FORM_DATA['title'])
        self.assertEqual(len(articles), 1)
        self.assertEqual(len(Step.objects.filter(article=articles[0])), 2)

        self.client.logout()

    def master_editor_see_the_report(self, report_type):
        """ Check if the master editor sees the report """
        self.client.login(username=USERS[4]['username'], password=USERS[4]['password'])

        response = self.client.get(reverse('master_editor_panel'))
        self.assertEqual(response.status_code, 200)

        if report_type == "new":
            self.assertContains(response, f'<td>Review new article &quot;{FORM_DATA["title"]}&quot;</td>')
            self.assertContains(response, '<td>system_automat</td>')
            self.assertContains(response, '<td>na opened</td>')
        elif report_type == "open":
            self.assertContains(response, f'<td>New report about article &quot;{FORM_DATA["title"]}&quot;</td>')
            self.assertContains(response, f'<td>{USERS[1]["username"]}</td>')
            self.assertContains(response, f'<td>opened</td>')

        self.client.logout()

    def editor_can_see_the_report(self, report_type):
        """ Check if the editor can't see the report """
        if report_type == "new":
            report = Report.objects.get(article__title=FORM_DATA["title"], author__username='system_automat')

            self.client.login(username=USERS[2]['username'], password=USERS[2]['password'])

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            if report.editor == self.test_users['editors'][0]:
                self.assertContains(response, f'<td>Review new article &quot;{FORM_DATA["title"]}&quot;</td>')
                self.assertContains(response, '<td>system_automat</td>')
                self.assertContains(response, '<td>new article</td>')
            else:
                self.assertNotContains(response, f'<td>Review new article &quot;{FORM_DATA["title"]}&quot;</td>')
                self.assertNotContains(response, '<td>system_automat</td>')
                self.assertNotContains(response, '<td>new article</td>')

            self.client.logout()

            self.client.login(username=USERS[3]['username'], password=USERS[3]['password'])

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            self.assertNotContains(response, f'<td>Review new article &quot;{FORM_DATA["title"]}&quot;</td>')
            self.assertNotContains(response, '<td>system_automat</td>')
            self.assertNotContains(response, '<td>new article</td>')

            self.client.logout()

        elif report_type == "open":
            report = Report.objects.get(article__title=FORM_DATA["title"], author__username=USERS[1]['username'])

            self.client.login(username=USERS[2]['username'], password=USERS[2]['password'])

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            if report.editor == self.test_users['editors'][0]:
                self.assertContains(response, f'<td>New report about article &quot;{FORM_DATA["title"]}&quot;</td>')
                self.assertContains(response, f'<td>{USERS[1]["username"]}</td>')
                self.assertContains(response, f'<td>assigned</td>')
            else:
                self.assertNotContains(response, f'<td>New report about article &quot;{FORM_DATA["title"]}&quot;</td>')
                self.assertNotContains(response, f'<td>{USERS[1]["username"]}</td>')
                self.assertNotContains(response, f'<td>assigned</td>')

            self.client.logout()

            self.client.login(username=USERS[3]['username'], password=USERS[3]['password'])

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            self.assertNotContains(response, f'<td>New report about article &quot;{FORM_DATA["title"]}&quot;</td>')
            self.assertNotContains(response, f'<td>{USERS[1]["username"]}</td>')
            self.assertNotContains(response, f'<td>opened</td>')

            self.client.logout()

    def user_create_report(self):
        """ Create the report about the existing article"""
        self.client.login(username=USERS[1]['username'], password=USERS[1]['password'])

        article = Article.objects.get(title=FORM_DATA['title'])
        report_data = {
            'description': f'New report about article "{FORM_DATA["title"]}"',
            'article': article,
        }

        report_form = ReportForm(report_data)
        self.assertTrue(report_form.is_valid(), f"report_form not valid: {report_form.errors}")
        response = self.client.post(reverse('report_article', args=[article.id]), data=report_form)

        self.assertRedirects(response, reverse('home'))
        reports = Report.objects.filter(description=report_data['description'])
        self.assertEqual(len(reports), 1)

        self.client.logout()

    def master_editor_assign_the_report(self):
        """ Assign the report to the editor """
        self.client.login(username=USERS[4]['username'], password=USERS[4]['password'])

        old_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        self.assertFalse(old_report.editor)

        assign_data = {
            'report_id': old_report.id,
            'editor_assign_id': User.objects.get(username=USERS[2]['username']).id,
        }

        response = self.client.post(reverse('master_editor_panel'), data=assign_data)
        self.assertRedirects(response, reverse('home'))

        report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        self.assertEqual(report.editor.username, USERS[2]['username'])

        self.client.logout()

    def editor_closes_report(self):
        """ Close the report by editor """
        self.client.login(username=USERS[2]['username'], password=USERS[2]['password'])

        old_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        close_report_data = {
            'close_report': 'Close Report',
        }

        response = self.client.post(reverse('manage_report', args=[old_report.id]), data=close_report_data)
        self.assertRedirects(response, reverse('home'))

        report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        if old_report.status == "changes applied":
            self.assertEqual(report.status, "concluded")
        elif old_report.status == "assigned":
            self.assertEqual(report.status, "rejected")

        self.client.logout()

    def editor_editing_article(self):
        """ Edit article by assigned editor """
        self.client.login(username=USERS[2]['username'], password=USERS[2]['password'])

        report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        article = Article.objects.get(id=report.article_id)

        edited_data = {
            'title': article.title,
            'tags': 'new_tag',
        }

        self.assertNotEquals(article.tags, edited_data['tags'])

        response = self.client.post(reverse('edit_article', args=[article.id]), data=edited_data)
        self.assertRedirects(response, reverse('home'))

        edited_article = Article.objects.get(id=report.article_id)
        self.assertEqual(list(edited_article.tags.values_list('name', flat=True)), edited_data['tags'].split(', '))

        edited_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        self.assertEqual(edited_report.status, 'changes applied')

        self.client.logout()

    def test_new_report_after_creating_article(self):
        # 1. User1 creates article
        self.user_create_article()
        # 2. Master Editor see the report
        self.master_editor_see_the_report("new")
        # 3. Editor1 can't see a report
        self.editor_can_see_the_report("new")

    def test_manual_report(self):
        # 1. User1 creates article
        self.user_create_article()
        # 2. User2 creates report
        # self.user_create_report()
        report = Report()
        report.description = f'New report about article "{FORM_DATA["title"]}"'
        report.author = self.test_users['users'][1]
        report.created_at = datetime.now()
        report.article = Article.objects.get(title=FORM_DATA["title"])
        report.status = 'opened'
        report.save()
        # 3. Master Editor see the report
        self.master_editor_see_the_report("open")
        # 4. Editor1 and Editor2 can't see a report
        self.editor_can_see_the_report("open")

    def test_assign_report(self):
        self.test_manual_report()
        # 5. Master Editor assigns the report
        self.master_editor_assign_the_report()
        # 6. Editor1 sees a report, Editor2 can't
        self.editor_can_see_the_report("open")

    def test_reject_report(self):
        self.test_assign_report()
        # 7. Editor1 closes a report without making any changes
        self.editor_closes_report()

    def test_conclude_report(self):
        self.test_assign_report()
        # 7. Editor1 id doing some edition in the article
        self.editor_editing_article()
        # 8. Editor1 closes a report after making changes
        self.editor_closes_report()

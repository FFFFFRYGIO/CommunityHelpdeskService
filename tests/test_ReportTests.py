from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse

from editor_app.forms import ReportForm
from editor_app.models import Report
from tests.MainTestBase import MainTestBase, USERS, FORM_DATA
from user_app.forms import StepFormSetCreate
from user_app.models import Article, Step


# Create your tests here.


class ReportsTests(MainTestBase):
    def user_create_article(self):
        """ Create article to be reported"""
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[0]['username'], 'password': USERS[0]['password']})
        self.assertRedirects(response, reverse('home'))

        step_form_set = StepFormSetCreate(FORM_DATA)
        self.assertTrue(step_form_set.is_valid(), f'step_form_set not valid: {step_form_set.errors}')
        response = self.client.post(reverse('create_article'), data=FORM_DATA)

        self.assertRedirects(response, reverse('home'))
        articles = Article.objects.filter(title=FORM_DATA['title'])
        self.assertEqual(len(articles), 1)
        self.assertEqual(len(Step.objects.filter(article=articles[0])), 2)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def master_editor_see_the_report(self, report_type):
        """ Check if the master editor sees the report """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[4]['username'], 'password': USERS[4]['password']})
        self.assertRedirects(response, reverse('home'))

        response = self.client.get(reverse('master_editor_panel'))
        self.assertEqual(response.status_code, 200)

        if report_type == 'new':
            self.assertContains(response, f'Review &quot;{FORM_DATA["title"]}&quot;')
            self.assertContains(response, 'system_automat')
            self.assertContains(response, 'na opened')
        elif report_type == 'open':
            report_title = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"').title
            self.assertContains(response, report_title.replace('"', '&quot;').replace("'", '&#x27;'))
            self.assertContains(response, f'{USERS[1]["username"]}')
            self.assertContains(response, f'opened')

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def editor_can_see_the_report(self, report_type):
        """ Check if the editor can't see the report """
        if report_type == "new":
            report = Report.objects.get(article__title=FORM_DATA['title'], author__username='system_automat')

            response = self.client.post(reverse('login'),
                                        data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
            self.assertRedirects(response, reverse('home'))

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            if report.editor == self.test_users['editors'][0]:
                self.assertContains(response, f'Review new article &quot;{FORM_DATA["title"]}&quot;')
                self.assertContains(response, 'system_automat')
                self.assertContains(response, 'new article')
            else:
                self.assertNotContains(response, f'Review new article &quot;{FORM_DATA["title"]}&quot;')
                self.assertNotContains(response, 'system_automat')
                self.assertNotContains(response, 'new article')

            response = self.client.post(reverse('logout'))
            self.assertRedirects(response, reverse('login'))

            response = self.client.post(reverse('login'),
                                        data={'username': USERS[3]['username'], 'password': USERS[3]['password']})
            self.assertRedirects(response, reverse('home'))

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            self.assertNotContains(response, f'Review new article &quot;{FORM_DATA["title"]}&quot;')
            self.assertNotContains(response, 'system_automat')
            self.assertNotContains(response, 'new article')

            response = self.client.post(reverse('logout'))
            self.assertRedirects(response, reverse('login'))

        elif report_type == 'open':
            report = Report.objects.get(article__title=FORM_DATA['title'], author__username=USERS[1]['username'])

            response = self.client.post(reverse('login'),
                                        data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
            self.assertRedirects(response, reverse('home'))

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            if report.editor == self.test_users['editors'][0]:
                report_title = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"').title
                self.assertContains(response, report_title.replace('"', '&quot;').replace("'", '&#x27;'))
                self.assertContains(response, f'{USERS[1]["username"]}')
                self.assertContains(response, f'assigned')
            else:
                report_title = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"').title
                self.assertNotContains(response, report_title.replace('"', '&quot;').replace("'", '&#x27;'))
                self.assertNotContains(response, f'{USERS[1]["username"]}')
                self.assertNotContains(response, f'Status: assigned')

            response = self.client.post(reverse('logout'))
            self.assertRedirects(response, reverse('login'))

            response = self.client.post(reverse('login'),
                                        data={'username': USERS[3]['username'], 'password': USERS[3]['password']})
            self.assertRedirects(response, reverse('home'))

            response = self.client.get(reverse('editor_panel'))
            self.assertEqual(response.status_code, 200)

            self.assertNotContains(response, f'<td>New report about article &quot;{FORM_DATA["title"]}&quot;</td>')
            self.assertNotContains(response, f'<td>{USERS[1]["username"]}</td>')
            self.assertNotContains(response, f'<td>opened</td>')

            response = self.client.post(reverse('logout'))
            self.assertRedirects(response, reverse('login'))

    def user_report_article(self):
        """ Create the report about the existing article"""
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[1]['username'], 'password': USERS[1]['password']})
        self.assertRedirects(response, reverse('home'))

        article = Article.objects.get(title=FORM_DATA['title'])
        report_data = {
            'description': f'New report about article "{FORM_DATA["title"]}"',
            'article': article,
        }

        report_form = ReportForm(report_data)
        self.assertTrue(report_form.is_valid(), f'report_form not valid: {report_form.errors}')
        response = self.client.post(reverse('report_article', args=[article.id]), data=report_form)

        self.assertRedirects(response, reverse('home'))
        reports = Report.objects.filter(description=report_data['description'])
        self.assertEqual(len(reports), 1)

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def master_editor_assign_the_report(self):
        """ Assign the report to the editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[4]['username'], 'password': USERS[4]['password']})
        self.assertRedirects(response, reverse('home'))

        report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        self.assertFalse(report.editor)

        assign_data = {
            'report_id': report.id,
            'editor_assign_id': User.objects.get(username=USERS[2]['username']).id,
        }

        response = self.client.post(reverse('manage_report', args=[report.id]), data=assign_data)
        self.assertRedirects(response, reverse('home'))

        report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        self.assertEqual(report.editor.username, USERS[2]['username'])

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def editor_closes_report(self):
        """ Close the report by editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
        self.assertRedirects(response, reverse('home'))

        old_report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')

        close_report_data = {
            'close_report': 'Close Report',
        }

        response = self.client.post(reverse('manage_report', args=[old_report.id]), data=close_report_data)
        self.assertRedirects(response, reverse('home'))

        report = Report.objects.get(description=f'New report about article "{FORM_DATA["title"]}"')
        if old_report.status == 'changes applied':
            self.assertEqual(report.status, 'concluded')
        elif old_report.status == 'assigned':
            self.assertEqual(report.status, 'rejected')

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def editor_editing_article(self):
        """ Edit article by assigned editor """
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
        self.assertRedirects(response, reverse('home'))

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

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_new_report_after_creating_article(self):
        # 1. User1 creates article
        self.user_create_article()
        # 2. Master Editor see the report
        self.master_editor_see_the_report('new')
        # 3. Editor1 can't see a report
        self.editor_can_see_the_report('new')

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
        self.master_editor_see_the_report('open')
        # 4. Editor1 and Editor2 can't see a report
        self.editor_can_see_the_report('open')

    def test_assign_report(self):
        self.test_manual_report()
        # 5. Master Editor assigns the report
        self.master_editor_assign_the_report()
        # 6. Editor1 sees a report, Editor2 can't
        self.editor_can_see_the_report('open')

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

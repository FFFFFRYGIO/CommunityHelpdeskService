from django.contrib.auth.models import User
from django.urls import reverse

from tests.AccessTestBase import AccessTestsBase
from tests.MainTestBase import USERS


# Create your tests here.


class MasterEditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[4]['username'], 'password': USERS[4]['password']})
        self.assertRedirects(response, reverse('home'))
        self.user = User.objects.get(username=self.test_users['master_editors'][0].username)

    def tearDown(self):
        super().tearDown()
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


del AccessTestsBase

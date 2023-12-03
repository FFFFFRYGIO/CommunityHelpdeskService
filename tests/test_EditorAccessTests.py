from django.contrib.auth.models import User

from tests.AccessTestBase import AccessTestsBase
from tests.MainTestBase import USERS

from django.urls import reverse


# Create your tests here.


class EditorAccessTests(AccessTestsBase):

    def setUp(self):
        super().setUp()
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[2]['username'], 'password': USERS[2]['password']})
        self.assertRedirects(response, reverse('home'))
        self.user = User.objects.get(username=self.test_users['editors'][0].username)

    def tearDown(self):
        super().tearDown()
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login') + "?next=" + reverse('logout'))


del AccessTestsBase

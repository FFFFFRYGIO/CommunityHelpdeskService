from django.contrib.auth.models import User
from django.urls import reverse

from tests.AccessTestBase import AccessTestsBase
from tests.MainTestBase import USERS


# Create your tests here.


class AuthenticatedUserAccessTests(AccessTestsBase):
    def setUp(self):
        response = self.client.post(reverse('login'),
                                    data={'username': USERS[0]['username'], 'password': USERS[0]['password']})
        self.assertRedirects(response, reverse('home'))
        self.user = User.objects.get(username=USERS[0]['username'])

    def tearDown(self):
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


del AccessTestsBase

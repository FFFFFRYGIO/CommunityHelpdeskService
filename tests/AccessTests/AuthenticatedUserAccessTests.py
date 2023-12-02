from .AccessTestBase import AccessTestsBase


# Create your tests here.


class AuthenticatedUserAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['users'][0])
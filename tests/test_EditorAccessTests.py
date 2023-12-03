from tests.AccessTestBase import AccessTestsBase


# Create your tests here.


class EditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['editors'][0])
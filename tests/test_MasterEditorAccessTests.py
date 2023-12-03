from tests.AccessTestBase import AccessTestsBase


# Create your tests here.


class MasterEditorAccessTests(AccessTestsBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.test_users['master_editors'][0])
from .AccessTestBase import AccessTestsBase


# Create your tests here.


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

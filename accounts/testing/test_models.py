from django.test import TestCase
from django.contrib.auth import get_user, get_user_model

class UserModelTest(TestCase):
    username = "test_user"
    password = "testing"

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = get_user_model().objects.create_user(username=cls.username, password=cls.password)

    def test_model_fields(self):
        self.assertEqual(self.user.username, self.username)


    def test_login(self):
        """
            is_authenticated() returns True or False correctly
        """
        self.client.login(username=self.username, password=self.password)
        logged_user = get_user(self.client)
        assert logged_user.is_authenticated
        self.assertEqual(logged_user.username, self.username)

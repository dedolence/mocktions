from django.test import SimpleTestCase, TestCase, Client, TransactionTestCase
from django.urls import reverse
from ..models import User
from .. import views
from django.core.exceptions import ObjectDoesNotExist
from psycopg2 import InterfaceError
from unittest.mock import patch


class IndexViewTest(SimpleTestCase):

    def test_url_exists_at_correct_location(self):
        """
            URL redirects according to its relative path.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        """
            URL redirects according to its reversale name property.
        """
        response = self.client.get(reverse("accounts:index"))
        self.assertEqual(response.status_code, 302)


    def test_url_redirects_user_not_logged_in(self):
        """
            Redirects an unauthenticated user to a login page.
        """
        response = self.client.get(reverse("accounts:index"))
        self.assertRedirects(response, reverse("accounts:login"))


class LoginViewTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(username="test_user", password="test_password")

    def test_url_exists_at_correct_location(self):
        """
            URL redirects according to its relative path.
        """
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        """
            URL redirects according to its reversale name property.
        """
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        """
            Loads the correct template.
        """
        response = self.client.get(reverse("accounts:login"))
        self.assertTemplateUsed('accounts/html/templates/login.html')

    def test_user_can_login(self):
        """
            Indirectly tests that a user is logged in by checking that the
            redirected URL is a profile page.
        """
        user = User.objects.get(pk=self.user.id)
        response = self.client.post(
            reverse("accounts:login"),
            {'username': "test_user", 'password': "test_password"}
        )
        self.assertIn(response.url, f"/accounts/profile/{user.id}")
        self.assertEqual(response.status_code, 302)


class LogoutViewTest(SimpleTestCase):

    def test_url_exists_at_correct_location(self):
        """
            URL redirects according to its relative path.
        """
        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        """
            URL redirects according to its reversale name property.
        """
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        """
            Loads the correct template.
        """
        response = self.client.get(reverse("accounts:logout"))
        self.assertTemplateUsed('accounts/html/templates/logout.html')


class DeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create_user(username="test_user1", password="test_password1")
        cls.user2 = User.objects.create_user(username="test_user2", password="test_password2")

    def test_url_exists_at_correct_location(self):
        self.client.login(username="test_user1", password="test_password1")
        user_id = self.user1.id
        response = self.client.get(f"/accounts/delete/{user_id}")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        self.client.login(username="test_user1", password="test_password1")
        user_id = self.user1.id
        response = self.client.get(reverse("accounts:delete_account", args=[user_id]))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        self.client.login(username="test_user1", password="test_password1")
        user_id = self.user1.id
        response = self.client.get(reverse("accounts:delete_account", args=[user_id]))
        self.assertTemplateUsed('accounts/html/templates/delete_account.html')

    def test_user_can_delete_their_own_account(self):
        self.client.raise_request_exception = False
        self.client.login(username="test_user1", password="test_password1")
        user = User.objects.get(username="test_user1")
        response = self.client.post(
            reverse("accounts:delete_account", args=[user.id]), 
            {'delete_confirmation': 'on'}
        )
        self.client.logout()
        self.assertNotIn(user, User.objects.all())

    def test_user_cannot_delete_others_account(self):
        self.client.raise_request_exception = False

        # Log in the first user
        self.client.login(username="test_user1", password="test_password1")

        # Then try to delete the second user from the first user's session
        user2 = User.objects.get(username="test_user2")

        # Normally the test_func from UserPassesTest mixin won't allow
        # accessing of another user's profile page. But just in case,
        # the patch deactivates the test and still tests whether one
        # user could delete another user's account.
        with patch.object(views.DeleteAccount, "test_func", return_value=True):
            self.client.post(
                reverse('accounts:delete_account', args=[user2.id]),
                {'delete_confirmation': 'on'},
            )
            self.assertIn(user2, User.objects.all())
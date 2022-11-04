from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse
from ..models import User
from django.core.exceptions import ObjectDoesNotExist


class DeleteViewTest(TestCase):
    """
        Things to check:
        - Can access URL
        - Template is rendered
        - Logged in user can delete their own account
        - User cannot delete another's account
        - After deleting, redirect with success message.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.client = Client()
        cls.user1 = User.objects.create_user(username="test_user1", password="test_password1")
        cls.user2 = User.objects.create_user(username="test_user2", password="test_password2")

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

    def test_user_can_delete_their_own_account(self):
        self.client.raise_request_exception = False
        self.client.login(username="test_user1", password="test_password1")
        user_id = self.user1.id
        self.client.post(
            reverse("accounts:delete_account", args=[user_id]),
            {'delete_confirmation': 'on'}
        )
        self.assertRaises(ObjectDoesNotExist, User.objects.get, pk=user_id)

    def test_user_cannot_delete_other_users_account(self):
        pass

    def test_user_must_be_logged_in(self):
        self.client.logout()
        user_id = self.user1.id
        self.client.post(
            reverse("accounts:delete_account", args=[user_id]),
            {'delete_confirmation': 'on'}
        )

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


class LoginViewTest(SimpleTestCase):

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

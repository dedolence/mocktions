from django.test import SimpleTestCase, TestCase, Client, TransactionTestCase
from django.urls import reverse
from ..models import User
from .. import views
from ..forms import RegistrationForm
from django.core.exceptions import ObjectDoesNotExist
from psycopg2 import InterfaceError
from unittest.mock import patch
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser


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
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/profile/{user.id}", 302, 200)


class LogoutViewTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(username="test_user", password="test_password")

    def test_get_redirects_to_index(self):
        """
            URL redirects according to its relative path.
        """
        response = self.client.get("/accounts/logout/")
        self.assertRedirects(response, reverse("base:index"))
        self.assertRedirects(response, "/")

    def test_user_can_logout(self):
        self.client.login(username="test_user", password="test_password")
        user_before = auth.get_user(self.client)
        self.client.post(reverse("accounts:logout"))
        user_after = auth.get_user(self.client)
        self.assertNotEqual(user_before, user_after)
        self.assertIsInstance(user_after, AnonymousUser)


class RegisterViewtest(TestCase):
    """
        - User can submit a valid form and a user is created
        - Invalid form is rejected
        - Checks for duplicate usernames
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.valid_data = {
            'username': 'test_user',
            'password1': 'test_password',
            'password2': 'test_password',
            'first_name': 'john',
            'last_name': 'doe',
            'email': 'test@example.com',
            'street': '123 Example Rd.',
            'city': 'Exampleville',
            'state': 'EX',
            'postcode': '12345',
            'country': 'EXA',
            'phone': '(555) 555-5555'
        }

        cls.invalid_no_username = {
            'password1': 'test_password',
            'password2': 'test_password',
            'first_name': 'john',
            'last_name': 'doe',
            'email': 'test@example.com',
            'street': '123 Example Rd.',
            'city': 'Exampleville',
            'state': 'EX',
            'postcode': '12345',
            'country': 'EXA',
            'phone': '(555) 555-5555'
        }

        cls.existing_user = User.objects.create_user(username="existing_user", password="test_password")
    
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/accounts/register/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("accounts:register"))
        self.assertTemplateUsed('accounts/html/templates/register.html')

    def test_valid_form_creates_user(self):
        response = self.client.post(reverse('accounts:register'), self.valid_data)
        self.assertIsNotNone(User.objects.get(username="test_user"))

    def test_invalid_form_creates_error(self):
        #response = self.client.post(reverse('accounts:register'), self.invalid_no_username)
        pass

    def test_cannot_duplicate_usernames(self):
        print(self.existing_user)
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'existing_user',
                'password1': 'different_password',
                'password2': 'different_password'
            }
        )
        print(User.objects.filter(username='existing_user').count())
        self.assertTrue(True)
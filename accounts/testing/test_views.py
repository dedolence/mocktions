from django.test import SimpleTestCase
from django.urls import reverse

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

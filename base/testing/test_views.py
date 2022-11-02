from django.http import HttpResponseServerError, HttpResponse
from django.test import SimpleTestCase, override_settings
from django.urls import path, reverse
from mocktions.settings import ROOT_URLCONF
from mocktions.urls import urlpatterns


def deliver_500(request):
    return 1/0

urlpatterns = [
    path('/test_500', deliver_500, name="deliver_500")
]


class TestIndexView(SimpleTestCase):

    def test_url_exists_at_correct_location(self):
        """
            URL redirects according to its relative path.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


    def test_template_is_used(self):
        """
            URL redirects according to its reversale name property.
        """
        response = self.client.get(reverse("base:index"))
        self.assertContains(response, "/staticfiles/images/gavel_icon")



@override_settings(ROOT_URLCONF='mocktions.urls')
class Test_404(SimpleTestCase):
    
    def test_return_404(self):
        response = self.client.get("/sojeijfois")
        self.assertEqual(response.status_code, 400)

    def test_render_custom_404_template(self):
        response = self.client.get("/aoseijfoaisejf")
        self.assertContains(response, "404 Error: Page not found", status_code=400)


@override_settings(ROOT_URLCONF=__name__)
class Test_500(SimpleTestCase):

    def test_return_500(self):
        self.client.raise_request_exception = False
        response = self.client.get(reverse('deliver_500'))
        self.assertEqual(response.status_code, 500)

    def test_render_custom_500_template(self):
        self.client.raise_request_exception = False
        response = self.client.get(reverse('deliver_500'))
        self.assertTemplateUsed("osijefoisej")
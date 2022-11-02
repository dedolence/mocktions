from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from mocktions.settings import ROOT_URLCONF
from django.urls import path
from django.shortcuts import render
from ..views import handler500


def raise_500(request):
    return 1/0

urlpatterns = [
    path('500/', raise_500),
]

handler500 = handler500


class TestIndexView(SimpleTestCase):

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


    def test_template_is_used(self):
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

    def test_handler_renders_template_response(self):
        self.client.raise_request_exception = False
        response = self.client.get('/500/')
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed('base/html/templates/500.html')
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from mocktions.settings import ROOT_URLCONF
from django.urls import path
from ..urls import urlpatterns
from ..strings import en


def raise_500(request):
    return 1/0

urlpatterns.append(path('raise_500', raise_500, name="raise_500"))


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
        self.assertContains(response, en.PAGE_NOT_FOUND_H, status_code=400)


class Test_500(SimpleTestCase):

    def test_handler_renders_template_response(self):
        self.client.raise_request_exception = False
        response = self.client.get(reverse('base:raise_500'))
        self.assertContains(response, en.SERVER_ERROR_H, status_code=500)
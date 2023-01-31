from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.urls import reverse_lazy
from mocktions.settings import AUTH_USER_MODEL as User

"""
    Things to test:
    User can enter a URL of an image.
        - non-image URLs are rejected
        - non-valid URLs are rejected
        - valid image URLs are retrieved and uploaded to user's account
    User can upload a file from their computer.
        - non-image files are rejected
        - images that are too large are rejected
    User can retrieve a random image.
"""

class UploadImageTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.user = User.objects.create_user(username="test_user", password="test_password")
        cls.test_image = open("test-image.jpeg", "r")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def test_successful_upload(self):
        request_data = {
            'image_field': self.test_image
        }
        response = self.client.post(reverse_lazy("images:add"), request_data)
        self.assertRedirects(
            response, 
            reverse_lazy("images:update", args=[1])
        )
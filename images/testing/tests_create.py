from unittest import mock

from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponse
from django.forms import ValidationError
from django.urls import reverse_lazy

from accounts.models import User
from images.models import Image, size_validator

from .tests_utility import BaseImageTestClass, create_image

class ImageCreateTests(BaseImageTestClass):

    add_url = reverse_lazy("images:add")

    def test_only_images_accepted(self):
        with open("images/testing/test_text.txt") as fp:
            response = self.login_and_post({'image_field': fp}, self.add_url)
            self.assertContains(
                response, 
                'The file you uploaded was either not an image or a corrupted image.'
            )

    def test_size_validator(self):
        class _file:
            def __init__(self) -> None:
                self.size = 100000000

        mock_iff = mock.Mock(ImageFieldFile)
        mock_iff._file = _file()

        self.assertRaises(
            ValidationError,
            size_validator,
            mock_iff
        )
        
    def test_picture_upload(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            self.assertLess(Image.objects.count(), 1)
            response = self.login_and_post({'image_field': fp}, self.add_url)
            self.assertGreaterEqual(Image.objects.count(), 1)

    def test_big_image_rejected(self):
        with open("images/testing/big_image.jpg", "rb") as fp:
            response = self.login_and_post({'image_field': fp}, self.add_url)
            self.assertContains(
                response,
                "Image is too large. Images must be less than"
            )
            self.assertIsNone(Image.objects.first())

    def test_must_be_logged_in(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            response = self.client.post(
                self.add_url,
                {'image_field': fp},
                follow=True
            )
            self.assertRedirects(
                response, 
                reverse_lazy("accounts:login") 
                + f"?next={reverse_lazy('images:add')}"
            )

    def test_image_owner_related_name(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            response = self.login_and_post({'image_field': fp}, self.add_url)
            img = Image.objects.first()
            user = User.objects.get(username=self.username)
            self.assertEquals(
                user.images.first(),
                img
            )

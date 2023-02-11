import os
from unittest import mock

from io import BytesIO
from django.db.models.fields.files import ImageFieldFile
from django.forms import ValidationError
from django.test import TestCase, override_settings
from django.http import HttpResponse

from accounts.models import User
from images.models import Image, size_validator
from django.urls import reverse_lazy
from django.conf import settings

from django.core.files.base import ContentFile
from PIL import Image as PILImage

def create_image(
        size: tuple[int, int] = (50,50), 
        ext = "png", 
        filename = "test_image.png"
    ) -> ContentFile:
    """
        https://stackoverflow.com/a/22824942/9137423
    """
    image_file = BytesIO()
    image = PILImage.new('RGBA', size=size, color=(256,0,0))
    image.save(image_file, "png")
    image_file.seek(0)
    django_file = ContentFile(image_file.read(), filename)
    return django_file

@override_settings(
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'mediafiles/tests')
)
class ImageCreateTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_upload_path = os.path.join(
            settings.BASE_DIR, 'mediafiles/tests'
        )
        cls.username = "test_user"
        cls.password = "test_password"
        cls.user: User = User.objects.create_user(
            username=cls.username, password=cls.password
        )

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        """
            Delete all temporary files
        """
        for img in Image.objects.all():
            img.delete()
            
        import glob
        directory = os.path.join(cls.temp_upload_path, 'user_uploads')
        os.chdir(directory)
        files = glob.glob('test*')
        for f in files:
            os.unlink(f)
        return super().tearDownClass()

    def setUp(self) -> None:
        for img in Image.objects.all():
            img.delete()
        return super().setUp()

    
    def login_and_post(self, form_data: dict) -> HttpResponse:
        self.client.login(
            username = self.username, 
            password = self.password
        )
        response = self.client.post(
            reverse_lazy("images:add"), 
            form_data,
            follow=True
        )
        return response

    def test_only_images_accepted(self):
        with open("images/testing/test_text.txt") as fp:
            response = self.login_and_post({'image_field': fp})
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
            response = self.login_and_post({'image_field': fp})
            self.assertGreaterEqual(Image.objects.count(), 1)

    def test_big_image_rejected(self):
        with open("images/testing/big_image.jpg", "rb") as fp:
            response = self.login_and_post({'image_field': fp})
            self.assertContains(
                response,
                "Image is too large. Images must be less than"
            )
            self.assertIsNone(Image.objects.first())

    def test_must_be_logged_in(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            response = self.client.post(
                reverse_lazy("images:add"),
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
            response = self.login_and_post({'image_field': fp})
            img = Image.objects.first()
            user = User.objects.get(username=self.username)
            self.assertEquals(
                user.images.first(),
                img
            )

""" 
class ImageUpdateTests(BaseImageTest):

    def test_must_own_image(self):
        # login and post an image to user1's account
        # logout. login as user2. attempt to edit user1's image.
        with open("images/testing/test_image.jpeg", "rb") as fp:
            user1 = User.objects.create_user(
                username = "test_user2",
                password = "test_user2"
            )
             """
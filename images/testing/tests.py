from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.urls import reverse_lazy
from accounts.models import User
from django.conf import settings
from PIL import Image as PILImage
import os
from io import BytesIO
from django.core.files.base import ContentFile
from images.models import Image
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
def create_image(size: tuple[int, int] = (50,50), ext = "png", filename = "test_image.png") -> ContentFile:
    """
        https://stackoverflow.com/a/22824942/9137423
    """
    image_file = BytesIO()
    image = PILImage.new('RGBA', size=size, color=(256,0,0))
    image.save(image_file, "png")
    image_file.seek(0)
    django_file = ContentFile(image_file.read(), filename)
    return django_file

@override_settings(MEDIA_ROOT = os.path.join(
            settings.BASE_DIR, 'mediafiles/tests'))
class UploadImageTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_upload_path = os.path.join(
            settings.BASE_DIR, 'mediafiles/tests'
        )
        cls.username = "test_user"
        cls.password = "test_password"
        cls.user = User.objects.create_user(
            username=cls.username, password=cls.password
        )
        
        cls.image_path = os.path.join(
            settings.BASE_DIR, 
            "images/testing/test-image.jpeg"
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


    def test_successful_upload(self):
        self.client.login(
            username = self.username, 
            password = self.password
        )

        form_data = {'image_field': create_image()}

        response = self.client.post(
            reverse_lazy("images:add"), 
            form_data,
            follow=True
        )

        self.assertRedirects(
            response, 
            reverse_lazy("images:update", args=[1])
        )

        self.assertEquals(
            Image.objects.count(), 1
        )
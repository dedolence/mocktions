import os
from io import BytesIO
from django.test import TestCase, override_settings
from django.http import HttpResponse

from accounts.models import User
from images.models import Image
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
class BaseImageTestClass(TestCase):
    
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

    
    def login_and_post(self, form_data: dict, url: str) -> HttpResponse:
        self.client.login(
            username = self.username, 
            password = self.password
        )
        response = self.client.post(
            url, 
            form_data,
            follow=True
        )
        return response
from .tests_utility import BaseImageTestClass
from django.urls import reverse_lazy
from images.models import Image
from accounts.models import User
from django.test import TestCase, TransactionTestCase

class HintClass(TransactionTestCase):
    """
        This exists purely so Pylance shows inherited properties from TestCase
        within its child classes... a little silly I know...
    """
    pass

class ImageDeleteClass(BaseImageTestClass, HintClass):

    def test_must_be_logged_in(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            self.login_and_post({'image_field': fp}, reverse_lazy("images:add"))
        
        self.client.logout()

        image = Image.objects.first()
        response = self.client.post(reverse_lazy("images:delete", args=[image.pk]))
        redirect_url = reverse_lazy("accounts:login") + f"?next=/images/{image.pk}/delete"
        self.assertRedirects(response, redirect_url)

    def test_can_only_delete_own_images(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            self.login_and_post({'image_field': fp}, reverse_lazy("images:add"))
            
        self.client.logout()

        image = Image.objects.first()
        username2 = "test_user2"
        password2 = "t3St_uSer!"
        user2 = User.objects.create_user(username=username2, password=password2)
        self.client.login(username=username2, password=password2)

        response = self.client.post(reverse_lazy("images:delete", args=[image.pk]))
        self.assertRedirects(response, reverse_lazy("base:index"))
        self.assertEqual(Image.objects.count(), 1)
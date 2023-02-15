from .tests_utility import BaseImageTestClass
from django.urls import reverse_lazy

class ImageDeleteClass(BaseImageTestClass):

    delete_url = reverse_lazy("images:delete")

    def test_must_be_logged_in(self):
        with open("images/testing/test_image.jpeg", "rb") as fp:
            response = self.login_and_post({'image_field': fp}, self.delete_url)
            self.client.logout()
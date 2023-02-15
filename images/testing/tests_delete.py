from .tests_utility import BaseImageTestClass
from django.urls import reverse_lazy

class ImageDeleteClass(BaseImageTestClass):

    delete_url = reverse_lazy("images:delete")

    def test_must_be_logged_in(self):
        response = self.client.post({

        })
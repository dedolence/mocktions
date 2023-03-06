from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.urls import reverse_lazy
from .models import Image
from django.forms import BaseModelForm
from typing import Any
from .forms import ImageUploadForm
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from images.strings.en import *
from django.template.loader import render_to_string
from images.forms import ImageUploadForm
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import requests
from time import sleep
from b2sdk.api import B2Api
from typing import TypedDict
from django.http import JsonResponse
from django.conf import settings
from django_backblaze_b2.storage import BackblazeB2Storage

class ImageCreateView(LoginRequiredMixin, CreateView):
    """
        Creates an Image model instance, saves it (which uploads it to B2 
        bucket), and returns a redirect to that image UpdateView.
    """
    template_name = "images/html/templates/add.html"
    model = Image
    form_class = ImageUploadForm

    def form_valid(self, form: BaseModelForm) -> http.HttpResponse:
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)


class ImageUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "images/html/templates/update.html"
    model = Image
    form_class = ImageUploadForm


class ImageDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    template_name = "images/html/templates/delete.html"
    model = Image
    success_url = reverse_lazy("images:index")
    success_message = "Image uploaded successfully!"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
            I do not want to support GET requests to delete images. However, I also do
            not want to return a 405 error by excluding GET from allowed_method_names, 
            because that returns a blank page (unless I create a middleware to catch 405
            errors and return a template - perhaps in the future).
        """
        return HttpResponseRedirect(reverse_lazy("base:index"))

    def get_object(self, queryset = None) -> Image:
        obj: Image = super().get_object(queryset)
        if self.request.user != obj.uploaded_by:
            return None
        return obj

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if self.object == None:
            messages.add_message(self.request, messages.WARNING, DELETE_PERMISSION_DENIED)
            return HttpResponseRedirect(reverse_lazy("base:index"))
        return super().post(request, *args, **kwargs)

class ImageListView(LoginRequiredMixin, ListView):
    template_name = "images/html/templates/index.html"
    model = Image


class TestPath(DetailView):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        sleep(2)
        return HttpResponse("Here is a message.")

class ImageAddInline(LoginRequiredMixin, CreateView):
    model = Image
    fields = ["image_field"]

    def form_valid(self, form: BaseModelForm) -> http.HttpResponse:
        form.instance.uploaded_by = self.request.user
        self.object = form.save()
        return HttpResponse(
            render_to_string(
                "images/html/includes/image.html", 
                {"image": self.object}, 
                self.request)
            )
    
def presigned_url(request):
    """
        Gets the storage class from settings (B2 Backblaze) and uses it to 
        access the B2 API to get and return a URL for uploading. Trying to
        access the B2 API directly isn't working, I'm not sure why.
    """
    b2_storage = BackblazeB2Storage()
    b2_app_key = settings.B2_APPLICATION_KEY
    b2_app_key_id = settings.B2_APPLICATION_KEY_ID
    b2_bucket_id = settings.B2_BUCKET_ID
    b2_realm = "https://api.backblazeb2.com"
    
    auth_dict = b2_storage.b2Api.raw_api.authorize_account(
        b2_realm, 
        b2_app_key_id, 
        b2_app_key
    )
    response_dict = b2_storage.b2Api.raw_api.get_upload_url(
        auth_dict['apiUrl'], 
        auth_dict['authorizationToken'], 
        b2_bucket_id
    )
    
    
    return JsonResponse({"url": response_dict["uploadUrl"]})
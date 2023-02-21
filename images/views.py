from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from .models import Image
from django.forms import BaseModelForm
from typing import Any
from .forms import ImageUploadForm
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from images.strings.en import *


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
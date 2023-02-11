from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from .models import Image
from django.forms import BaseModelForm
from typing import Any
from .forms import ImageUploadForm


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


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "images/html/templates/delete.html"
    model = Image
    success_url = reverse_lazy("images:index")

class ImageListView(LoginRequiredMixin, ListView):
    template_name = "images/html/templates/index.html"
    model = Image
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from .models import Image
from django.forms import BaseModelForm

class ImageCreateView(LoginRequiredMixin, CreateView):
    template_name = "images/html/templates/add.html"
    model = Image
    fields = ["image_field"]

    def form_valid(self, form: BaseModelForm) -> http.HttpResponse:
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)


class ImageUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "images/html/templates/update.html"
    model = Image
    fields = ["image_field"]


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "images/html/templates/delete.html"
    model = Image
    success_url = reverse_lazy("images:index")

class ImageListView(LoginRequiredMixin, ListView):
    template_name = "images/html/templates/index.html"
    model = Image
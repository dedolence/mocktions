from django.shortcuts import render
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ImageUploadForm

class IndexView(FormView, LoginRequiredMixin):
    form_class = ImageUploadForm
    template_name = "images/html/templates/index.html"
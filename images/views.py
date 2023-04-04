from django.views.generic import CreateView
from images.models import Image
from django.http import HttpRequest, HttpResponse
from typing import Any
from django.shortcuts import render
from images.test.test_form import TestForm
from django.template.loader import render_to_string


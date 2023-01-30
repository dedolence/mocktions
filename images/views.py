import environ, os, boto3
from botocore.config import Config
from pathlib import Path
from django import http
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from mocktions.settings import BASE_DIR, USE_LOCAL
from typing import Dict, Any

class IndexView(TemplateView):
    template_name = "images/html/templates/index.html"
    
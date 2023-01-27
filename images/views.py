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
    def get(
            self, request: http.HttpRequest, *args: Any, **kwargs: Any
        ) -> http.HttpResponse:
        
        if USE_LOCAL:
            return http.HttpResponseRedirect(reverse_lazy("base:index"))
        else:
            # set up django-environ to read environment variables
            env = environ.Env(
                DEBUG=(bool, False)
            )

            environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
            B2_KEY_ID = env('B2_KEY_ID')
            B2_KEY_NAME = env('B2_KEY_NAME')
            B2_APPLICATION_KEY = env('B2_APPLICATION_KEY')
            B2_BUCKET_ENDPOINT = env('B2_BUCKET_ENDPOINT')
            B2_RESOURCE = boto3.resource(
                service_name = 's3',
                endpoint_url = B2_BUCKET_ENDPOINT,
                aws_access_key_id = B2_KEY_ID,
                aws_secret_access_key = B2_APPLICATION_KEY,
                config = Config(
                    signature_version='s3v4',
                )
            )
            return super().get(request, *args, **kwargs)
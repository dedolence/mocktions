import pathlib
from uuid import uuid4
from django.urls import reverse
from django.http import JsonResponse
import os, json, boto3
from django.shortcuts import render
from .forms import UploadImageForm
from mocktions.settings.base import STATIC_URL
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string

def index(request):
    form = UploadImageForm()
    return render(request, 'images/html/templates/index.html', {
        'form': form
    })


def get_image_html(request):
    image_url = request.GET.get('image_url', None)
    if image_url is None:
        image_url = staticfiles_storage.url('images/image_not_found.png')
    html = render_to_string('images/html/includes/image_thumbnail.html', {
        'image_url': image_url
    })
    return JsonResponse({'html': html})


def post_image(request):
    pass


def sign_s3(request):
    """
        Generates a pre-signed post object that allows uploading an image to S3 bucket.
    """
    AWS_BUCKET = os.environ['AWS_BUCKET_NAME']
    AWS_REGION = os.environ['AWS_REGION']
    file = request.POST.get('file_name', 'untitled')
    file_extension = pathlib.Path(file).suffix
    if file_extension is None:
        file_extension = 'jpg'
    unique_file_name = f"{uuid4().hex}{file_extension}"
    image_url = 'https://{b}.s3.{r}.amazonaws.com/static/images/{i}'.format(
        b = AWS_BUCKET,
        r = AWS_REGION,
        i = unique_file_name)

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket = AWS_BUCKET,
        Key = "static/images/" + unique_file_name,
        ExpiresIn = 3600,
    )

    return JsonResponse({'data': presigned_post, 'image_url': image_url})
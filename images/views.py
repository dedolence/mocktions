import pathlib
from uuid import uuid4
from django.urls import reverse
from django.http import JsonResponse
import os, json, boto3
from django.shortcuts import render
from .forms import UploadImageForm
from mocktions.settings.base import STATIC_URL

def index(request):
    form = UploadImageForm()
    return render(request, 'images/html/templates/index.html', {
        'form': form
    })


def post_image(request):
    pass


def sign_s3(request):
    AWS_BUCKET = os.environ['AWS_BUCKET_NAME']
    AWS_REGION = os.environ['AWS_REGION']
    file = request.POST.get('file_name', 'untitled')
    file_extension = pathlib.Path(file).suffix
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
from django.urls import reverse
from django.http import JsonResponse
import os, json, boto3
from django.shortcuts import render
from .forms import UploadImageForm

try:
    from mocktions.settings.dev import STATIC_URL
except KeyError:
    from mocktions.settings.prod import STATIC_URL

def index(request):
    form = UploadImageForm()
    return render(request, 'images/html/templates/index.html', {
        'form': form
    })


def post_image(request):
    pass


def sign_s3(request):
    S3_BUCKET = os.environ['AWS_BUCKET_NAME']
    file_name = request.POST.get('file_name', 'untitled')
    file_type = request.POST.get('file_type', 'image/jpeg')
    url = f"https://{STATIC_URL}/images/{file_name}"

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = {'acl': 'public-read', 'Content-Type': file_type},
        Conditions = [
            {'acl': 'public-read'},
            {'Content-Type': file_type},
        ],
        ExpiresIn = 3600,
    )

    return JsonResponse({'data': presigned_post, 'url': url})
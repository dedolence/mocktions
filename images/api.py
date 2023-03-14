from rest_framework import status, permissions, generics, parsers
from rest_framework.response import Response
from images.models import Image
from images.serializers import ImageUploadSerializer, ImageURLSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
import urllib.request

from typing import Any

from time import sleep
        
class ImageViewSet(viewsets.ModelViewSet):
    """
        For use with HTMX, therefore all API responses are rendered as
        HTML.

        GET returns a rendered form for uploading images.
        POST returns the form for more uploads, along with any errors.
    """
    serializer_class = ImageUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    renderer_classes = [TemplateHTMLRenderer]
    

    def get_queryset(self):
        """
            For now, filter images by the user. This can be modified to
            filter by post as well.
        """
        return self.request.user.images.all()
     

    def list(self, request):
        upload_serializer = ImageUploadSerializer()
        url_serializer = ImageURLSerializer()
        images = self.get_queryset()
        return Response(
            {
                'upload_serializer': upload_serializer, 
                'url_serializer': url_serializer,
                'images': images
            },
            template_name = "images/html/templates/index.html"
        )
    

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(**{'uploaded_by': request.user})
        
        return Response(
            {'images': self.get_queryset(), 'serializer': serializer},
            template_name = "images/html/includes/image_list.html", 
            status=status.HTTP_201_CREATED,
        )


    @action(methods=["POST"], detail=False)
    def upload(self, request):
        upload_serializer = ImageUploadSerializer(data=request.data)
        url_serializer = ImageURLSerializer()

        if upload_serializer.is_valid():
            upload_serializer.save(**{'uploaded_by': request.user})

        return Response({
                'upload_serializer': upload_serializer, 
                'url_serializer': url_serializer,
                'images': self.get_queryset()
            }, template_name="images/html/includes/image_list.html")
    

    @action(methods=["POST"], detail=False)
    def fetch(self, request):
        upload_serializer = ImageUploadSerializer()
        url_serializer = ImageURLSerializer(data=request.data)

        if url_serializer.is_valid():
            url = url_serializer.data["url"]
            img_temp = NamedTemporaryFile(delete=True)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
            req = urllib.request.Request(url=url, headers=headers)
            img_temp.write(urlopen(req).read())
            img_temp.flush()

            image = Image(uploaded_by = request.user)
            image.image_field.save("random.jpg", File(img_temp))
            image.save()

        return Response({
            'upload_serializer': upload_serializer, 
            'url_serializer': url_serializer,
            'images': self.get_queryset()
        }, template_name="images/html/includes/image_list.html")


    def retrieve(self, request, *args, **kwargs):
        return Response(
            {'images': [self.get_object()]}, 
            template_name="images/html/templates/update.html"
        )
    

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


    @action(methods=["POST"], detail=True)
    def post_destroy(self, request, pk=None):
        """
            the DRF action "destroy" only supports incoming requests with
            the DELETE method (as opposed to POST/GET/etc.). that method is
            unavailable to HTML forms. so here is a way to delete model
            instances that accepts POST requests.
        """
        obj = self.get_object()
        obj.delete()
        return HttpResponseRedirect(reverse_lazy("images:image-list"))

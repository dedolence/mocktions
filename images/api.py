from rest_framework import status
from rest_framework.response import Response
from images.models import Image
from images.serializers import ImageUploadSerializer, ImageURLSerializer, ImageAltSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
import urllib.request

        
class ImageViewSet(viewsets.ModelViewSet):
    """
        For use with HTMX, therefore all API responses are rendered as
        HTML.

        GET returns a rendered form for uploading images.
        POST returns the form for more uploads, along with any errors.
    """
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

        if upload_serializer.is_valid():
            image = upload_serializer.save(**{'uploaded_by': request.user})
        
        return self.dispatch_html(request, image, upload_serializer=upload_serializer)
    

    @action(methods=["POST"], detail=False)
    def fetch(self, request):
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

        return self.dispatch_html(request, image, url_serializer=url_serializer)


    def retrieve(self, request, *args, **kwargs):
        return Response(
            {'image': self.get_object()}, 
            template_name="images/html/includes/update.html"
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
    

    def dispatch_html(self, 
        request, 
        image, 
        upload_serializer = ImageUploadSerializer(),
        url_serializer = ImageURLSerializer()):
        """
            A convenience function to return the correct template that the 
            HTMX scripts expect on the client side.
        """
        return Response(
            {
                'upload_serializer': upload_serializer, 
                'url_serializer': url_serializer,
                'image': image,
            },
            template_name="images/html/includes/upload_response.html",
        )

    @action(methods=["POST"], detail=True)
    def update_alt(self, request, *args, **kwargs):
        """
            Performs a partial update using POST method.
        """
        serializer = ImageAltSerializer(data=request.data)
        if serializer.is_valid():
            obj = self.get_object()
            obj.alt = serializer.data["alt"]
            print(obj.__dict__)
            obj.save()
            message = "Changes saved!"
        else:
            message = "Error saving changes: " + serializer.errors["alt"][0]

        return Response(
                data = {"message": message},
                template_name = "images/html/templates/toast_message.html",
                headers = {'HX-Trigger': "displayToast"},
            )
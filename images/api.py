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
from urllib import request as requests

from typing import List
        
class HX_ImageViewSet(viewsets.ModelViewSet):
    """
        For use with HTMX, therefore all API responses are rendered as
        HTML.

        GET returns a widget that can be included in other pages that 
        includes a form for uploading as well as an output list of 
        image thumbnails.

        The purpose is to allow images to be attached (via foreign key)
        to model instances like Users (for avatars), blog posts, or, in
        my case, auction listings. 

        To help link uploaded images with their related model instance,
        each time an image is uploaded it adds an <option> to a hidden
        <select> input that contains the ID value of the image, and these
        IDs are submitted with the rest of the model creation form.

        To accomplish this, add the following HTML to the form:
        <select id="id_image_upload_list" class="d-none" hx-swap-oob="afterbegin"></select>

        Upon uploading, HTMX will look for an element with ID "id_image_upload_list" and
        append an <option name="image_upload" value="{{ image.id }}" multiiple/> element 
        to it.

        Within that <select> element, add in any already-uploaded images however
        you want, e.g. providing a dict called "images" and a for loop:
        {% for image in images %}<option name="image_upload" value="{{ image.id }}" selected/>{% endfor %}
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
        return self.dispatch_html(request)
    

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(**{'uploaded_by': request.user})
        
        return Response(
            {'images': self.get_queryset(), 'serializer': serializer},
            template_name = "images/html/includes/main.html", 
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
            image = Image.objects.create(uploaded_by=request.user)
            response = requests.urlretrieve(url)
            image.image_field.save("random.jpeg", File(open(response[0], 'rb')))
            image.save()

        return self.dispatch_html(request, image, url_serializer=url_serializer)


    def retrieve(self, request, *args, **kwargs):
        return Response(
            {'image': self.get_object()}, 
            template_name="images/html/templates/update.html"
        )
    

    @action(methods=["POST"], detail=True)
    def post_destroy(self, request, pk=None):
        """
            the DRF action "destroy" only supports incoming requests with
            the DELETE method (as opposed to POST/GET/etc.). that method is
            unavailable to HTML forms. so here is a way to delete model
            instances that accepts POST requests.
        """
        message = ""
        img_id = None
        try:
            obj = self.get_object()
            if request.user != obj.uploaded_by:
                raise PermissionError("Could not delete image: permission denied.")
            img_id = obj.id
            obj.delete()
            message = "Image deleted."
        except PermissionError as e:
            message = e

        return Response(
                data = {"message": message, "img_id": img_id},
                template_name = "images/html/templates/toast_message.html",
                headers = {'HX-Trigger': "displayToast"},
            )
    

    def dispatch_html(self, 
        request, 
        instance: Image | List[Image] | None = None, 
        upload_serializer: ImageUploadSerializer | None = ImageUploadSerializer(),
        url_serializer: ImageURLSerializer | None = ImageURLSerializer()):
        """
            A convenience function to return the correct template that the 
            HTMX scripts expect on the client side.
        """
        if instance:
            try:
                # doesn't change anything if instance is already a list
                images = list(instance)
            except TypeError:
                # converts to list if it wasn't already.
                images = [instance]
        else:
            images = None
        
        return Response(
            {
                'upload_serializer': upload_serializer, 
                'url_serializer': url_serializer,
                'images': images,
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
            obj.save()
            message = "Changes saved!"
        else:
            message = "Error saving changes: " + serializer.errors["alt"][0]

        return Response(
                data = {"message": message},
                template_name = "images/html/templates/toast_message.html",
                headers = {'HX-Trigger': "displayToast"},
            )
    

    @action(methods=["GET"], detail=False)
    def set_order(self, request):
        try:
            order_list = request.query_params.getlist("image")
            for i in range(len(order_list)):
                img = Image.objects.get(pk=order_list[i])
                img.order = i
                img.save()
            return Response(
                data = {"message": "Changes saved!"},
                template_name = "images/html/templates/toast_message.html",
                headers = {'HX-Trigger': "displayToast"},
            )
        except:
            return Response(
                data = {"message": "There was an error saving changes."},
                template_name = "images/html/templates/toast_message.html",
                headers = {'HX-Trigger': "displayToast"},
            )